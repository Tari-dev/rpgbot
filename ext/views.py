from typing import Optional
import discord

__all__ = ("StopChildDisabledView", "TimeOutDisableView")

class StopChildDisabledView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)

    def stop(self) -> None:
        for child in self.children:
            child.disabled = True
            super().stop()

class TimeOutDisableView(StopChildDisabledView):
    def __init__(self, *, timeout: float | None = 180):
        self.response = Optional[discord.InteractionMessage] = None
        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        self.stop()
        if self.response:
            await self.response.edit(view=None)
        return await super().on_timeout()