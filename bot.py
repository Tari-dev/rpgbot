import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional, Union

import aiohttp
import discord
import motor.motor_asyncio
from discord.ext import commands
from dotenv import load_dotenv

import ext

load_dotenv()

TOKEN = os.environ['TOKEN']
MONGO_URL = os.environ['MONGO_URL']


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"


logger = ext.log.create_logger(level=logging.INFO)

TEST_GUILD = discord.Object(id=1214922874825998346)
COGS = [
    "cogs.basic",
    "jishaku"
]




class RPGBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            case_insensitive=True,
            intents=discord.Intents.default(),
            activity=discord.Activity(name="new users using /help", type=discord.ActivityType.watching),
            owner_id=615785223296253953,
        )
        self.loop = asyncio.get_running_loop()
        self._ready = asyncio.Event()
        self.real_db = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        self.session = aiohttp.ClientSession()

    @property
    def db(self):
        return self.real_db.rpgbot

    async def on_ready(self):
        if not hasattr(self, 'launch_time'):
            self.launch_time = datetime.now(timezone.utc)

        if hasattr(self, 'cluster'):
            logger.info(f'Logged in as {self.user}')
            logger.info(f'Cluster {self.cluster.id}: {self.shard_ids}')
        else:
            logger.info(f'Logged in as {self.user}')

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    def get_nested_command(
        self, name: str, guild: Optional[discord.Guild]
    ) -> Optional[Union[discord.app_commands.Command, discord.app_commands.Group]]:
        """
        Get nested command of given command. If Guild is given, searches for guild specific command
        Parameters
        -------------
        name: str
        guild: Optional[:class: `discord.Guild`]

        Returns
        ---------
        Optional[Union[:class: `discord.app_commands.Command`, :class: `discord.app_commands.Group`]]
            The Command or ``None`` if not found.
        """
        key, *keys = name.split(' ')
        cmd = self.tree.get_command(key, guild=guild) or self.tree.get_command(key)

        for key in keys:
            if cmd is None:
                return None
            if isinstance(cmd, discord.app_commands.Command):
                break

            cmd = cmd.get_command(key)

        return cmd

    @discord.app_commands.command(name="help")
    async def _help(self, interaction: discord.Interaction, command: str):
        cmd = self.get_nested_command(command, guild=interaction.guild)
        if cmd is None:
            await interaction.response.send_message(f'Could not find a command named {command}', ephemeral=True)
            return

        description = (
            cmd.callback.__doc__ or cmd.description
            if isinstance(cmd, discord.app_commands.Command)
            else cmd.__doc__ or cmd.description
        )

        embed = discord.Embed(title=cmd.title, description=description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.autocomplete()
    async def help_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[discord.app_commands.Choice[str]]:
        commands = list(self.tree.walk_commands(guild=None, type=discord.AppCommandType.chat_input))

        if interaction.guild is not None:
            commands.extend(self.tree.walk_commands(guild=interaction.guild, type=discord.AppCommandType.chat_input))

        choices: List[discord.app_commands.Choice[str]] = []
        for command in commands:
            name = command.qualified_name
            if current in name:
                choices.append(discord.app_commands.Choice(name=name, value=name))

        # Only show unique commands
        choices = sorted(set(choices), key=lambda c: c.name)
        return choices[:25]

    async def close(self) -> None:
        await self.session.close()
        return await super().close()


async def main():
    bot = RPGBot()
    for cog in COGS:
        await bot.load_extension(cog)
    await bot.start(TOKEN, reconnect=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
