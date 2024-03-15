from enum import Enum
import discord
from discord import app_commands, ui
from discord.ext import commands

class Elements(Enum):
    none = 0
    fire = 1
    earth = 2
    water = 3
    air = 4

class ElementalView(ui.View):
    def __init__(self):
        self.value: Elements = Elements.none
        super().__init__(timeout=60)

    @ui.button(label="fire", emoji="🔥", row=0)
    async def fire_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(f"You have chosen {self.value.name}", view=self)

    @ui.button(label="earth", emoji="🪨", row=1)
    async def earth_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(f"You have chosen {self.value.name}", view=self)

    @ui.button(label="water", emoji="🫧", row=2)
    async def water_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(f"You have chosen {self.value.name}", view=self)

    @ui.button(label="air", emoji="🌪", row=3)
    async def air_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(f"You have chosen {self.value.name}", view=self)

    def stop(self) -> None:
        for child in self.children:
            child.disabled = True
            super().stop()

class BasicCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="attune")
    async def start(self, interaction: discord.Interaction):
        """This command starts off your adventure by letting you choose which element you use."""
        view = ElementalView()

        user_data = await self.bot.db.users.find_one({"_id": interaction.user.id})
        if user_data is None:
            await interaction.response.send_message(
                "***Welcome to the elemental magic RPG Bot, Conduit!\n***"
                "Choose which element you want to use, or in other words which conduit you choose to attune to.\n\n", 
                view=view
            )
            await view.wait()
            if view.value is Elements.none:
                return await interaction.followup.send("Please chose an element")
            else:
                await self.bot.db.users.insert_one({"_id": interaction.user.id, "element": view.value.value})

        else:
            element = Elements(user_data['element'])
            await interaction.response.send_message(
                f"You have already chosen **{element.name}**, if you wish to change this you will have to reset your stats using the `/reset` command"
            )


    @app_commands.command(name="reset")
    async def reset(self, interaction: discord.Interaction):
        """Deletes your bot progress"""
        await interaction.response.send_message("Done")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BasicCog(bot))
