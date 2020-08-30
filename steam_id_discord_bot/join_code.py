from discord.ext import commands

import log_conf
from persistance import User

logger = log_conf.get_logger(__name__)


async def log_and_send(channel, message):
    try:
        await channel.send(message)
    except Exception as e:
        logger.error(f'unable to send message {message!r}', exc_info=e)
    else:
        logger.info(repr(message))


def format_join_string(user, compact=False):
    uname = user.uname
    if compact:
        output = f"/join {user.steam_id} ({uname})"
    else:
        body, uname = f"/join {user.steam_id}", f" {uname} "
        output = f"{uname:-^{len(body)}}\n{body}"
    return output


class JoinCode(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'logged in as {self.bot.user!r}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    @commands.command(name='register')
    async def register(self, ctx, steam_id: str):
        defaults = {'name': ctx.author.name,
                    'discriminator': ctx.author.discriminator,
                    'steam_id': steam_id}
        user, created = User.get_or_create(discord_id=ctx.author.id,
                                           defaults=defaults)
        if created:
            message = f"registered Steam ID {steam_id!r} with {user.uname!r}"
        else:
            User.update(name=defaults['name'],
                        discriminator=defaults['discriminator'])
            message = f"updated {user.uname!r} with Steam ID {steam_id!r}"

        await log_and_send(ctx.message.channel, message)

    @commands.command(name='id')
    async def get_jump_code(self, ctx, name: str = None):
        if name is None:
            return await log_and_send(ctx.message.channel, body)

        users = list(User.search_from_input(name))
        if len(users) == 0:
            body = f"No user registered with {name!r}"
        elif len(users) == 1:
            body = f"```{format_join_string(users[0])}```"
        else:
            body = "Multiple Users Found (consider adding a discriminator):\n"
            body += '\n'.join(f"{format_join_string(u, True)}" for u in users)
            body = f"```{body}```"

        await log_and_send(ctx.message.channel, body)
