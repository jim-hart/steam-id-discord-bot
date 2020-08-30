from decouple import config
from discord.ext import commands

from join_code import JoinCode


def main():
    bot = commands.Bot(command_prefix='!')
    bot.add_cog(JoinCode(bot))
    bot.run(config('CLIENT_TOKEN'))


if __name__ == '__main__':
    main()
