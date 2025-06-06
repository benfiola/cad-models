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
    Pos,
    Rectangle,
    RegularPolygon,
    RigidJoint,
    Rot,
    Vector,
    add,
    extrude,
)

from cad_models.common import Model, ServerRackMountBlank, U, main
from cad_models.models.keystone_receiver import KeystoneReceiver


class GenericRpiTray(Model):
    def __init__(self, **kwargs):
        # parameters
        with BuildPart(mode=Mode.PRIVATE):
            base_keystone = KeystoneReceiver()
        dimensions = Vector(145.03 * MM, 1 * U, 154 * MM)
        hex_grid_count = Vector(11, 13)
        hex_grid_radius = 3 * MM
        hex_grid_spacing = 0.5 * MM
        interface_holes = Vector(2, 2)
        interface_thickness = 6 * MM
        keystone_offset = 56 * MM
        keystone_spacing = 23 * MM
        lip_thickness = 2.0 * MM
        rpi_cable_diameter = 4 * MM
        rpi_dimensions = Vector(71 * MM, 35 * MM, 101 * MM)
        rpi_magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        rpi_magnet_standoff_dimensions = Vector(10 * MM, 10 * MM, 7 * MM)
        rpi_magnet_standoff_spacing = 81 * MM
        rpi_offset = 17 * MM
        rpi_power_switch_dimensions = Vector(62.5 * MM, 19.6 * MM)
        rpi_power_switch_spacing = 5 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            # create blank
            blank = ServerRackMountBlank(
                dimensions=dimensions, interface_holes=interface_holes
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

            # create tray mount
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                location *= Pos(X=-rpi_offset)
                location *= Pos(Y=rpi_power_switch_dimensions.Y)
                location *= Pos(Y=rpi_power_switch_spacing)
                location *= Pos(Y=rpi_dimensions.Z / 2)
                with Locations(location) as locs:
                    tray_local_location = locs.local_locations[0]
                    tray_location = locs.locations[0]
                    Rectangle(
                        rpi_dimensions.X,
                        rpi_dimensions.Z,
                    )
                location = Location((0, -face.width / 2))
                location *= Pos(X=-rpi_offset)
                location *= Pos(Y=rpi_power_switch_dimensions.Y / 2)
                with Locations(location) as locs:
                    rpi_power_switch_location = locs.locations[0]
                    Rectangle(
                        rpi_power_switch_dimensions.X, rpi_power_switch_dimensions.Y
                    )
            tray_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)

            # create magnet standoffs
            with BuildSketch(face):
                with Locations(tray_local_location):
                    with GridLocations(rpi_magnet_standoff_spacing, 0, 2, 1):
                        Rectangle(
                            rpi_magnet_standoff_dimensions.X,
                            rpi_magnet_standoff_dimensions.Y,
                        )
            magnet_standoffs = extrude(amount=rpi_magnet_standoff_dimensions.Z)
            faces = magnet_standoffs.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-2:]
            for face in faces:
                with BuildSketch(face):
                    Circle(rpi_magnet_dimensions.X / 2)
                extrude(amount=-rpi_magnet_dimensions.Y, mode=Mode.SUBTRACT)

            # create tray mount joint
            face = tray_mount.faces().sort_by(Axis.Z)[0]
            location = tray_location
            RigidJoint(f"rpi", joint_location=location)

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

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericRpiTray())
