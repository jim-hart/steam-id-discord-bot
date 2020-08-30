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

    @commands.command(name='linkid')
    async def register(self, ctx, steam_id: str):
        if not steam_id.isnumeric():
            await log_and_send(ctx.message.channel, "Invalid Seam ID")
            return

        defaults = {'name': ctx.author.name,
                    'discriminator': ctx.author.discriminator,
                    'steam_id': steam_id}
        user, created = User.get_or_create(discord_id=ctx.author.id,
                                           defaults=defaults)
        if created:
            message = f"registered Steam ID {steam_id!r} with {user.uname!r}"
        else:
            for k, v in defaults.items():
                setattr(user, k, v)
            user.save()
            message = f"updated {user.uname!r} with Steam ID {steam_id!r}"

        await log_and_send(ctx.message.channel, message)

    @commands.command(name='id')
    async def get_jump_code(self, ctx, name: str = None):
        if name is None:
            query = User.select().where(User.discord_id == ctx.author.id)
        else:
            query = User.search_from_input(name)

        users = list(query)
        if len(users) == 0:
            name = ctx.author.name if name is None else name
            body = f"{name!r} has not registered their Steam ID"
        elif len(users) == 1:
            body = f"```{format_join_string(users[0])}```"
        else:
            body = "Multiple Users Found (consider adding a discriminator):\n"
            body += '\n'.join(f"{format_join_string(u, True)}" for u in users)
            body = f"```{body}```"

        await log_and_send(ctx.message.channel, body)
