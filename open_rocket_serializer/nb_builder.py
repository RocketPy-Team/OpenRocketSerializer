import json
import logging
import os

import nbformat as nbf

logger = logging.getLogger(__name__)


class NotebookBuilder:
    """Class that takes a parameters.json file and creates a jupyter notebook
    using rocketpy simulation on it
    """

    def __init__(self, parameters_json: str) -> None:
        """read the file and process the dictionary do not build anything yet"""
        self.parameters_json = parameters_json
        self.read()
        self.process()

    def read(self) -> dict:
        # read the json file and return the dict and save it to self.parameters dict
        # if any problem happens here, already tell the user
        with open(self.parameters_json, "r", encoding="utf-8") as f:
            self.parameters = json.load(f)
        return self.parameters

    def process(self):
        # TODO: read the dict and search for any inconsistencies
        return self.parameters

    def build(self, destination: str):
        nb = nbf.v4.new_notebook()
        nb = self.build_header(nb)
        nb = self.build_imports(nb)
        nb = self.build_environment(nb)
        nb = self.build_motor(nb)
        nb = self.build_rocket(nb)
        nb = self.build_flight(nb)
        self.save_notebook(nb, destination)
        logger.info(
            "[NOTEBOOK BUILDER] Notebook successfully built! You can find it at: %s",
            destination,
        )

    def build_header(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # create the first commentary cell
        text = "# RocketPy Simulation\n"
        text += "This notebook was generated using Rocket-Serializer, a RocketPy"
        text += " tool to convert simulation files to RocketPy simulations\n"
        text += (
            "The notebook was generated using the following parameters file: "
            + f"{self.parameters_json}\n"
        )

        nb["cells"] = [nbf.v4.new_markdown_cell(text)]
        logger.info("[NOTEBOOK BUILDER] Header created")
        return nb

    def build_imports(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # install rocketpy
        text = "%pip install rocketpy<=2.0\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # import classes
        text = (
            "from rocketpy import Environment, SolidMotor, Rocket, Flight, "
            + "TrapezoidalFins, RailButtons, NoseCone, Tail\n"
        )
        text += "import datetime\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))
        logger.info("[NOTEBOOK BUILDER] Imports section created")
        return nb

    def build_environment(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # add a markdown cell
        text = "## Environment\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # add a code cell
        text = "env = Environment()\n"
        text += (
            f"env.set_location(latitude={self.parameters['environment']['latitude']}, "
            + f"longitude={self.parameters['environment']['longitude']})\n"
        )
        text += f"env.set_elevation({self.parameters['environment']['elevation']})\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # add a markdown cell
        text = "Optionally, you can set the date and atmospheric model\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # add a code cell
        text = "tomorrow = datetime.date.today() + datetime.timedelta(days=1)\n"
        text += "env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))\n"
        text += "env.set_atmospheric_model(type='Forecast', file='GFS')"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # add a code cell
        text = "env.all_info()\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Environment section created")
        return nb

    def build_motor(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # start section and give comments
        text = "## Motor\n"
        text += "Currently, only Solid Motors are supported by Rocket-Serializer\n"
        text += "If you want to use a Liquid or Hybrid motor, please use rocketpy directly.\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # define the motor
        text = "motor = SolidMotor(\n"
        text += f"    thrust_source='{self.parameters['motors']['thrust_source']}',\n"
        text += f"    dry_mass={self.parameters['motors']['dry_mass']},\n"
        text += (
            "    center_of_dry_mass_position="
            + f"{self.parameters['motors']['center_of_dry_mass']},\n"
        )
        text += (
            "    dry_inertia="
            + f"{'[' + str(self.parameters['motors']['dry_inertia'])[1:-1] + ']'},\n"
        )
        text += (
            "    grains_center_of_mass_position="
            + f"{self.parameters['motors']['grains_center_of_mass_position']},\n"
        )
        text += f"    grain_number={self.parameters['motors']['grain_number']},\n"
        text += f"    grain_density={self.parameters['motors']['grain_density']},\n"
        text += f"    grain_outer_radius={self.parameters['motors']['grain_outer_radius']},\n"
        text += (
            "    grain_initial_inner_radius="
            + f"{self.parameters['motors']['grain_initial_inner_radius']},\n"
        )
        text += f"    grain_initial_height={self.parameters['motors']['grain_initial_height']},\n"
        text += (
            f"    grain_separation={self.parameters['motors']['grain_separation']},\n"
        )
        text += f"    nozzle_radius={self.parameters['motors']['nozzle_radius']},\n"
        text += f"    burn_time={self.parameters['motors']['burn_time']},\n"
        text += f"    nozzle_position={self.parameters['motors']['nozzle_position']},\n"
        text += f"    throat_radius={self.parameters['motors']['throat_radius']},\n"
        text += (
            "    reshape_thrust_curve=False,  # Not implemented in Rocket-Serializer\n"
        )
        text += "    interpolation_method='linear',\n"
        text += (
            "    coordinate_system_orientation="
            + f"'{self.parameters['motors']['coordinate_system_orientation']}',\n"
        )
        text += ")\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # see the outputs
        text = "motor.all_info()\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Motor section created")
        return nb

    def build_rocket(self, nb: nbf.v4.new_notebook):
        # add a markdown cell
        text = "## Rocket\n"
        text += (
            "Currently, only single stage rockets are supported by Rocket-Serializer\n"
        )
        text += "We will start by defining the aerodynamic surfaces, and then build the rocket.\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        self.build_all_aerodynamic_surfaces(nb)

        # define the Rocket
        text = "rocket = Rocket(\n"
        text += f"    radius={self.parameters['rocket']['radius']},\n"
        text += f"    mass={self.parameters['rocket']['mass']},\n"
        text += f"    inertia={'[' + str(self.parameters['rocket']['inertia'])[1:-1] + ']'},\n"
        text += f"    power_off_drag='{self.parameters['rocket']['drag_curve']}',\n"
        text += f"    power_on_drag='{self.parameters['rocket']['drag_curve']}',\n"
        text += (
            "    center_of_mass_without_motor="
            + f"{self.parameters['rocket']['center_of_mass_without_propellant']},\n"
        )
        text += (
            "    coordinate_system_orientation="
            + f"'{self.parameters['rocket']['coordinate_system_orientation']}',\n"
        )
        text += ")\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # add surfaces to rocket
        self.add_surfaces_to_rocket(nb)

        # add the motor to the rocket
        # TODO: kinda needs to fix this
        text = (
            "rocket.add_motor(motor, position= "
            + f"{self.parameters['rocket']['radius']})\n"
        )
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # add a code cell
        text = "### Rocket Info\n"
        text += "rocket.all_info()\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Rocket section created")
        return nb

    def build_all_aerodynamic_surfaces(
        self, nb: nbf.v4.new_notebook
    ) -> nbf.v4.new_notebook:
        """This is simple: receive the current notebook object, start appending
        cells for each aerodynamic surface and return the notebook object"""
        self.build_nosecones(nb)
        self.build_trapezoidal_fins(nb)
        self.build_tails(nb)
        self.build_rail_buttons(nb)

        logger.info("[NOTEBOOK BUILDER] All aerodynamic surfaces created.")
        return nb

    def add_surfaces_to_rocket(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # add a markdown cell
        text = "### Adding surfaces to the rocket\n"
        text += "Now that we have all the surfaces, we can add them to the rocket\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # add a code cell
        text = "rocket.add_surfaces"

        return nb

    def build_nosecones(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        """Generates a section defining the nosecone and returns the notebook."""
        # add a markdown cell
        text = "### Nosecones\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # Assumption: only a single nosecone to be added
        text = "nosecone = NoseCone(\n"
        text += f"    length={self.parameters['nosecones']['length']},\n"
        text += f"    kind='{self.parameters['nosecones']['kind']}',\n"
        text += f"    base_radius={self.parameters['rocket']['radius']},\n"
        text += f"    rocket_radius={self.parameters['rocket']['radius']},\n"
        text += (
            f"    name='{self.parameters['nosecones']['length']}',\n"  # TODO: fix this
        )
        text += ")\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Nosecone created.")
        return nb

    def build_trapezoidal_fins(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # add a markdown cell
        text = "### Fins\n"
        text += "As rocketpy allows for multiple fins sets, we will create a "
        text += "dictionary with all the fins sets and then add them to the rocket\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # add a code cell
        text = "trapezoidal_fins = {}\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))
        for i in range(len(self.parameters["trapezoidal_fins"])):
            text = f"trapezoidal_fins[{i}] = TrapezoidalFins(\n"
            text += f"    n={self.parameters['trapezoidal_fins'][str(i)]['number']},\n"
            text += f"    root_chord={self.parameters['trapezoidal_fins'][str(i)]['root_chord']},\n"
            text += f"    tip_chord={self.parameters['trapezoidal_fins'][str(i)]['tip_chord']},\n"
            text += f"    span={self.parameters['trapezoidal_fins'][str(i)]['span']},\n"
            text += f"    cant_angle={self.parameters['trapezoidal_fins'][str(i)]['cant_angle']},\n"
            text += (
                "    sweep_length="
                + f"{self.parameters['trapezoidal_fins'][str(i)]['sweep_length']},\n"
            )
            text += (
                "    sweep_angle="
                + f"{self.parameters['trapezoidal_fins'][str(i)]['sweep_angle']},\n"
            )
            text += f"    rocket_radius={self.parameters['rocket']['radius']},\n"  # TODO: fix this
            text += (
                f"    name='{self.parameters['trapezoidal_fins'][str(i)]['name']}',\n"
            )
            text += ")\n\n"
            nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Trapezoidal fins created.")
        return nb

    def build_tails(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        # add a markdown cell
        text = "### Transitions (Tails)\n"
        text += "As rocketpy allows for multiple tails, we will create a "
        text += "dictionary with all the tails and then add them to the rocket\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # add a code cell
        text = "tails = {}\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))
        for i in range(len(self.parameters["tails"])):
            text = f"tails[{i}] = Tail(\n"
            text += (
                f"    top_radius={self.parameters['tails'][str(i)]['top_radius']},\n"
            )
            text += f"    bottom_radius={self.parameters['tails'][str(i)]['bottom_radius']},\n"
            text += f"    length={self.parameters['tails'][str(i)]['length']},\n"
            text += f"    rocket_radius={self.parameters['rocket']['radius']},\n"
            text += f"    name='{self.parameters['tails'][str(i)]['name']}',\n"
            text += ")\n"
            nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Tails created.")
        return nb

    def build_rail_buttons(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        logger.info("rail buttons not implemented yet")
        return nb

    def build_flight(self, nb: nbf.v4.new_notebook) -> nbf.v4.new_notebook:
        """Generates a section defining the flight and returns the notebook."""
        # add a markdown cell
        text = "## Flight\n"
        text += "We will now create the flight simulation. Let's go!\n"
        nb["cells"].append(nbf.v4.new_markdown_cell(text))

        # add a code cell
        text = "flight = Flight(\n"
        text += "    rocket=rocket,\n"
        text += "    environment=env,\n"
        text += f"    rail_length={self.parameters['flight']['rail_length']},\n"
        text += f"    inclination={self.parameters['flight']['inclination']},\n"
        text += f"    heading={self.parameters['flight']['heading']},\n"
        text += "    terminate_on_apogee=False,\n"
        text += "    max_time=600,\n"
        text += ")"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        # add a code cell
        text = "flight.all_info()\n"
        nb["cells"].append(nbf.v4.new_code_cell(text))

        logger.info("[NOTEBOOK BUILDER] Flight section created.")
        return nb

    def save_notebook(self, nb: nbf.v4.new_notebook, destination: str) -> None:
        """Writes the .ipynb file to the destination folder. Also applies black
        formatting to the file to improve readability."""
        out_file = destination + "/simulation.ipynb"

        nbf.write(nb, out_file)
        logger.info("[NOTEBOOK BUILDER] Notebook saved to '%s'", out_file)

        # apply black formatting after saving (requires black[jupyter])
        os.system(f"black {out_file}")
        logger.info("[NOTEBOOK BUILDER] Black formatting applied to the final notebook")