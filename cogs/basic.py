from enum import Enum
from typing import Optional

import discord
from discord import app_commands, ui
from discord.ext import commands

from ext.views import TimeOutDisableView


class Elements(Enum):
    none = 0
    fire = 1
    earth = 2
    water = 3
    air = 4


class ConfirmView(TimeOutDisableView):
    def __init__(self):
        self.value: bool = 0
        super().__init__(timeout=60)

    @ui.button(label="Yes", style=discord.ButtonStyle.red)
    async def yes_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value: bool = 1
        self.stop()
        await interaction.response.send_message(f"Sad to see it... Your progress has been deleted.")

    @ui.button(label="No", style=discord.ButtonStyle.grey)
    async def no_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value: bool = 0
        self.stop()
        await interaction.response.send_message(f"Phew, good luck on your adventures!")


class ElementalView(TimeOutDisableView):
    def __init__(self):
        self.value: Elements = Elements.none
        super().__init__(timeout=60)

    @ui.button(label="fire", emoji="🔥", row=0)
    async def fire_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(
            f"You have become a conduit for the element of passion and destruction, you have chosen, **{self.value.name}**."
        )

    @ui.button(label="earth", emoji="🪨", row=0)
    async def earth_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(
            f"You have become a conduit for the element of spirituality and transformation, you have chosen, **{self.value.name}**."
        )

    @ui.button(label="water", emoji="🫧", row=1)
    async def water_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(
            f"You have become a conduit for the element of freedom and spontaneous, you have chosen {self.value.name}."
        )

    @ui.button(label="air", emoji="🌪", row=1)
    async def air_button(self, interaction: discord.Interaction, button: ui.Button) -> None:
        self.value = Elements[button.label]
        self.stop()
        await interaction.response.send_message(
            f"You have become a conduit for the element of roots and resilience, you hav chosen **{self.value.name}**."
        )


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
                view=view,
            )
            view.response = await interaction.original_response()
            await view.wait()
            if view.value is Elements.none:
                return await interaction.followup.send("You haven't chosen any element")
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
        view = ConfirmView()
        await interaction.response.send_message(
            "Are you sure you want to reset your progress with the bot? All of your stats will be deleted.", view=view
        )
        view.response = await interaction.original_response()
        await view.wait()
        await self.bot.db.users.delete_one({"_id": interaction.user.id})


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BasicCog(bot))
