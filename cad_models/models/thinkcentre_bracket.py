from copy import copy

from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    add,
    extrude,
    mirror,
)

from cad_models.common import Model, ServerRackMountBracket, U, main
from cad_models.models.keystone_receiver import KeystoneReceiver


class ThinkcentreBracket(Model):
    def __init__(
        self,
        flipped_joints: bool = False,
        keystone_receivers: bool = True,
        power_supply_tray: bool = False,
        **kwargs,
    ):
        # parameters
        dimensions = Vector(145.55 * MM, 1 * U, 189.5 * MM)
        face_thickness = 4 * MM
        with BuildPart(mode=Mode.PRIVATE):
            base_keystone = KeystoneReceiver()
        keystone_spacing = 25 * MM
        interface_holes = Vector(3, 2)
        cable_diameter = 4.1 * MM
        cable_slot_width = 3.8 * MM
        cable_tray_dimensions = Vector(20 * MM, 10 * MM, 70 * MM)
        power_supply_tray_dimensions = Vector(65 * MM, 6 * MM, 145 * MM)
        tray_offset = 12.5 * MM
        tray_thickness = 2 * MM

        with BuildPart() as builder:
            # create bracket
            bracket = ServerRackMountBracket(
                dimensions=dimensions,
                interface_holes=interface_holes,
                flipped_joints=flipped_joints,
            )
            builder.joints.update(bracket.joints)

            if keystone_receivers:
                # create keystone cutouts
                face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
                with BuildSketch(face):
                    with GridLocations(keystone_spacing, 0, 2, 1) as grid_locs:
                        keystone_locations = grid_locs.locations
                        Rectangle(
                            base_keystone.dimensions.X, base_keystone.dimensions.Y
                        )
                extrude(amount=-face_thickness, mode=Mode.SUBTRACT)

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

            if power_supply_tray:
                # find inner corner of rib
                face = builder.faces().filter_by(Axis.Z).group_by(Axis.Z)[-3][0]
                edge = face.edges().filter_by(Axis.X)[0]
                base_location = edge.location_at(0.0)
                base_location.orientation = face.orientation

                # create tray bases
                with BuildSketch(base_location):
                    # power supply
                    width = power_supply_tray_dimensions.X + tray_thickness
                    height = (
                        tray_offset
                        + tray_thickness
                        + power_supply_tray_dimensions.Z
                        + tray_thickness
                    )
                    Rectangle(width, height, align=Align.MIN)

                    location = Location((0, 0))
                    location *= Pos(X=power_supply_tray_dimensions.X)
                    location *= Pos(X=tray_thickness)
                    with Locations(location):
                        width = cable_tray_dimensions.X + tray_thickness
                        height = (
                            tray_offset
                            + tray_thickness
                            + cable_tray_dimensions.Z
                            + tray_thickness
                        )
                        Rectangle(width, height, align=Align.MIN)
                extrude(amount=-face_thickness)

                # create power supply tray solid
                with BuildSketch(base_location):
                    location = Location((0, 0))
                    location *= Pos(Y=tray_offset)
                    with Locations(location):
                        width = power_supply_tray_dimensions.X + tray_thickness
                        height = (
                            tray_thickness
                            + power_supply_tray_dimensions.Z
                            + tray_thickness
                        )
                        Rectangle(width, height, align=Align.MIN)
                solid = extrude(amount=power_supply_tray_dimensions.Y)

                # create power supply tray cutout
                face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
                with BuildSketch(face):
                    location = Location((-face.length / 2, -face.width / 2))
                    location *= Pos(Y=tray_thickness)
                    with Locations(location) as locs:
                        Rectangle(
                            power_supply_tray_dimensions.X,
                            power_supply_tray_dimensions.Z,
                            align=(Align.MIN, Align.MIN),
                        )
                extrude(amount=-power_supply_tray_dimensions.Y, mode=Mode.SUBTRACT)

                # create cable tray solid
                with BuildSketch(base_location):
                    location = Location((0, 0))
                    location *= Pos(X=power_supply_tray_dimensions.X)
                    location *= Pos(X=tray_thickness)
                    location *= Pos(Y=tray_offset)
                    with Locations(location):
                        width = cable_tray_dimensions.X + tray_thickness
                        height = (
                            tray_thickness + cable_tray_dimensions.Z + tray_thickness
                        )
                        Rectangle(width, height, align=Align.MIN)
                solid = extrude(amount=cable_tray_dimensions.Y)

                # create cable tray cutout
                face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
                with BuildSketch(face):
                    location = Location((-face.length / 2, -face.width / 2))
                    location *= Pos(Y=tray_thickness)
                    with Locations(location) as locs:
                        Rectangle(
                            cable_tray_dimensions.X,
                            cable_tray_dimensions.Z,
                            align=(Align.MIN, Align.MIN),
                        )
                extrude(amount=-cable_tray_dimensions.Y, mode=Mode.SUBTRACT)

                # create cable tray cable slots
                face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
                with BuildSketch(face):
                    Circle(cable_diameter / 2)
                    Rectangle(
                        cable_slot_width,
                        cable_tray_dimensions.Y,
                        align=(Align.CENTER, Align.MIN),
                    )
                solid = extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)
                mirror_plane = Plane(face).offset(
                    -((cable_tray_dimensions.Z / 2) + tray_thickness)
                )
                mirror(solid, mirror_plane, mode=Mode.SUBTRACT)
        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(ThinkcentreBracket(keystone_receivers=False, power_supply_tray=True))
