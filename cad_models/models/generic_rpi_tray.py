from copy import copy

from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    HexLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RegularPolygon,
    RigidJoint,
    Rot,
    Vector,
    add,
    extrude,
    fillet,
    mirror,
)

from cad_models.common import (
    Model,
    ServerRackMountBlank,
    U,
    filter_by_edge_length,
    main,
)
from cad_models.models.keystone_receiver import KeystoneReceiver


class GenericRpiTray(Model):
    def __init__(self, interface_hole_captive_nut: bool = False, **kwargs):
        # parameters
        with BuildPart(mode=Mode.PRIVATE):
            base_keystone = KeystoneReceiver()
        dimensions = Vector(145.03 * MM, 1 * U, 154 * MM)
        hex_grid_count = Vector(11, 13)
        hex_grid_radius = 3 * MM
        hex_grid_spacing = 0.5 * MM
        interface_holes = Vector(2, 2)
        keystone_offset = 56 * MM
        keystone_spacing = 23 * MM
        lip_thickness = 2.0 * MM
        rpi_power_cable_diameter = 4 * MM
        rpi_dimensions = Vector(71 * MM, 35 * MM, 101 * MM)
        rpi_magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        rpi_magnet_offset = 0.25 * MM
        rpi_magnet_standoff_corner_radius = 2.0 * MM
        rpi_magnet_standoff_dimensions = Vector(9.5 * MM, 10 * MM, 7 * MM)
        rpi_offset = 17 * MM
        rpi_power_switch_slot_corner_radius = 0.75 * MM
        rpi_power_switch_dimensions = Vector(62.5 * MM, 19.6 * MM)
        rpi_power_switch_inset = 3.5
        rpi_power_switch_spacing = 5 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            # create blank
            blank = ServerRackMountBlank(
                dimensions=dimensions,
                interface_hole_captive_nut=interface_hole_captive_nut,
                interface_holes=interface_holes,
            )
            builder.joints.update(blank.joints)

            # create tray
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            depth = (
                rpi_power_switch_dimensions.Y
                + rpi_power_switch_spacing
                + rpi_dimensions.Z
                + lip_thickness
            )
            with BuildSketch(face):
                thickness = tray_thickness + lip_thickness
                location = Location((0, face.width / 2))
                with Locations(location):
                    Rectangle(face.length, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=depth)

            # create rpi mount
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            tray_face = face
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(X=-rpi_offset)
                location *= Pos(Y=rpi_power_switch_dimensions.Y)
                location *= Pos(Y=rpi_power_switch_spacing)
                location *= Pos(Y=rpi_dimensions.Z / 2)
                with Locations(location) as locs:
                    rpi_mount_local_location = locs.local_locations[0]
                    rpi_mount_location = locs.locations[0]
                    Rectangle(
                        rpi_dimensions.X,
                        rpi_dimensions.Z,
                    )
            rpi_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)

            # create magnet standoffs
            face = tray_face
            with BuildSketch(face):
                location = rpi_mount_local_location
                location *= Pos(X=-rpi_dimensions.X / 2)
                location *= Pos(X=-rpi_magnet_standoff_dimensions.X / 2)
                with Locations(location):
                    Rectangle(
                        rpi_magnet_standoff_dimensions.X,
                        rpi_magnet_standoff_dimensions.Y,
                    )
            solid = extrude(amount=rpi_magnet_standoff_dimensions.Z)
            edges = solid.edges().filter_by(Axis.Z).group_by(Axis.X)
            rpi_magnet_standoff_fillet_edges = edges[0]
            face = rpi_mount.faces().sort_by(Axis.X)[0]
            mirror_plane = Plane(face).offset(-rpi_dimensions.X / 2)
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            solid = mirror(solid, mirror_plane)
            edges = solid.edges().filter_by(Axis.Z).group_by(Axis.X)
            rpi_magnet_standoff_fillet_edges.extend(edges[-1])
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=rpi_magnet_offset)
                with Locations(location):
                    Circle(rpi_magnet_dimensions.X / 2)
            solid = extrude(amount=-rpi_magnet_dimensions.Y, mode=Mode.SUBTRACT)
            mirror(solid, mirror_plane, mode=Mode.SUBTRACT)

            # create rpi mount joint
            face = rpi_mount.faces().sort_by(Axis.Z)[0]
            location = rpi_mount_location
            RigidJoint(f"rpi", joint_location=location)

            # create power switch mount
            height = lip_thickness + rpi_power_cable_diameter
            face = tray_face
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(X=-rpi_offset)
                location *= Pos(Y=lip_thickness)
                location *= Pos(Y=rpi_power_switch_dimensions.Y / 2)
                with Locations(location) as locs:
                    width = rpi_power_switch_dimensions.X + lip_thickness
                    length = rpi_power_switch_dimensions.Y + lip_thickness
                    Rectangle(width, length)
            solid = extrude(amount=height)
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            depth = height + rpi_power_switch_inset
            with BuildSketch(face):
                Rectangle(rpi_power_switch_dimensions.X, rpi_power_switch_dimensions.Y)
            solid = extrude(amount=-depth, mode=Mode.SUBTRACT)
            face = solid.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(Y=lip_thickness)
                location *= Pos(Y=rpi_power_cable_diameter / 2)
                with Locations(location):
                    Circle(rpi_power_cable_diameter / 2)
                location = Location((0, -face.width / 2))
                slot_width = rpi_power_cable_diameter / 2
                slot_height = lip_thickness + rpi_power_cable_diameter / 2
                with Locations(location):
                    Rectangle(slot_width, slot_height, align=(Align.CENTER, Align.MIN))
            solid = extrude(amount=lip_thickness, mode=Mode.SUBTRACT)
            mirror_plane = Plane(face).offset(-rpi_power_switch_dimensions.X / 2)
            mirror(solid, mirror_plane, mode=Mode.SUBTRACT)
            edge_length = lip_thickness / 2
            rpi_power_switch_slot_fillet_edges = (
                builder.edges()
                .filter_by(Axis.X)
                .filter_by(filter_by_edge_length(edge_length))
                .group_by(Axis.Z)
            )[2]

            # create hex grid
            face = (
                builder.part.faces()
                .filter_by(Axis.Z)
                .sort_by(Axis.Z)[1:3]
                .sort_by(Axis.Y)[1]
            )
            with BuildSketch(face):
                with HexLocations(
                    hex_grid_radius + hex_grid_spacing,
                    int(hex_grid_count.X),
                    int(hex_grid_count.Y),
                ):
                    RegularPolygon(hex_grid_radius, 6)
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

            # create face cutouts
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                # create mount cutout
                location = Location((0, face.width / 2))
                location *= Pos(X=rpi_offset)
                location *= Pos(Y=-(tray_thickness + lip_thickness))
                width = rpi_dimensions.X - (lip_thickness * 2)
                height = rpi_dimensions.Y - (lip_thickness * 2)
                with Locations(location):
                    Rectangle(width, height, align=(Align.CENTER, Align.MAX))

                # create keystone cutouts
                location = Location((0, 0))
                location *= Pos(X=-keystone_offset)
                location *= Pos(X=lip_thickness)
                location *= Pos(X=base_keystone.dimensions.Y / 2)
                with Locations(location):
                    with GridLocations(keystone_spacing, 0, 2, 1) as grid_locs:
                        keystone_locations = grid_locs.locations
                        Rectangle(
                            base_keystone.dimensions.X, base_keystone.dimensions.Y
                        )
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

            # attach keystone receivers to cutouts
            for index, keystone_location in enumerate(keystone_locations):
                joint_location = Location(keystone_location)
                joint_location *= Rot(Z=180)
                cutout_joint = RigidJoint(
                    f"keystone-{index}", joint_location=joint_location
                )
                keystone = copy(base_keystone)
                joint: RigidJoint = keystone.joints["keystone"]
                cutout_joint.connect_to(joint)
                add(keystone)

            # fillet edges
            fillet(rpi_magnet_standoff_fillet_edges, rpi_magnet_standoff_corner_radius)
            fillet(
                rpi_power_switch_slot_fillet_edges, rpi_power_switch_slot_corner_radius
            )
        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericRpiTray())
