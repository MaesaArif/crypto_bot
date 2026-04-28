import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

from google.cloud import bigquery
from google.oauth2 import service_account

import crypto_service

load_dotenv("secret/.env")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def get_bigquery_client(credentials_path=None):
    """Initialize BigQuery client using service account credentials."""
    # credentials_path = os.getenv("GCP_CREDENTIALS_PATH")
    if credentials_path and os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        return bigquery.Client(credentials=credentials, project=credentials.project_id)
    else:
        return bigquery.Client()


def query_bigquery(query: str, limit: int = 10):
    """Execute a BigQuery SQL query and return results."""
    client = get_bigquery_client("secret/discord-bot-484904-2dc07a5b046e.json")
    query_with_limit = f"{query}\nLIMIT {limit}"

    try:
        query_job = client.query(query_with_limit)
        results = query_job.result()

        rows = []
        for row in results:
            rows.append(dict(row))

        return rows, None
    except Exception as e:
        return None, str(e)


def format_results(rows: list, title: str = "Query Results"):
    """Format query results as a Discord embed."""
    if not rows:
        return discord.Embed(
            title=title, description="No results found.", color=discord.Color.blue()
        )

    embed = discord.Embed(
        title=title, description=f"Found {len(rows)} row(s)", color=discord.Color.blue()
    )

    for row in rows:
        value = ""
        for key, val in row.items():
            value += f"**{key}**: {val}\n"
        embed.add_field(name="", value=value or "Empty", inline=False)

    embed.set_footer(text=f"Queried at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return embed


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"{bot.user} has connected to Discord!")


@bot.tree.command(name="helloworldzzz", description="Says hello!")
async def helloworld(interaction: discord.Interaction):
    """A hello world slash command."""
    await interaction.response.send_message("Hello World!")


@bot.tree.command(name="pingcrypto", description="Check if the bot is responsive.")
async def ping(interaction: discord.Interaction):
    """Check if the bot is responsive."""
    await interaction.response.send_message("Pong! 🏓")


@bot.tree.command(
    name="crypto", description="Get latest crypto price data from BigQuery."
)
async def crypto(interaction: discord.Interaction, crypto_id: str = "bitcoin"):
    """Get latest crypto price data from BigQuery."""

    with open("query/Discord Crypto Bot Data Pull v1.sql") as f:
        query = f.read()

    await interaction.response.defer()
    rows, error = query_bigquery(query, limit=5)

    if error:
        await interaction.followup.send(f"❌ Error querying BigQuery: {error}")
        return

    if not rows:
        await interaction.followup.send(f"No data found for `{crypto_id}`")
        return

    embed = discord.Embed(
        title=f"📊 {crypto_id.capitalize()} Price Data",
        description=f"Latest {len(rows)} record(s)",
        color=discord.Color.gold(),
    )

    for row in rows:
        timestamp = row.get("timestamp", "N/A")
        currency = row.get("currency", "N/A")
        price = row.get("current_price", "N/A")

        embed.add_field(
            name=f"⏰ {timestamp}",
            value=f"**Currency**: {currency}\n**Price**: {int(price)}\n",
            inline=False,
        )

    embed.set_footer(
        text=f"Data from BigQuery • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await interaction.followup.send(embed=embed)


# @bot.tree.command(
#     name="query", description="Execute a custom SQL query on BigQuery (admin only)."
# )
# async def query_command(interaction: discord.Interaction, sql: str):
#     """Execute a custom SQL query on BigQuery (admin only)."""
#     admin_role_name = os.getenv("DISCORD_ADMIN_ROLE", "admin")

#     # Check if user has administrator permissions or the admin role
#     is_admin = interaction.user.guild_permissions.administrator or any(
#         admin_role_name.lower() in role.name.lower() for role in interaction.user.roles
#     )

#     if not is_admin:
#         await interaction.response.send_message(
#             "❌ You don't have permission to run custom queries.", ephemeral=True
#         )
#         return

#     if len(sql) > 1000:
#         await interaction.response.send_message(
#             "❌ Query too long (max 1000 characters).", ephemeral=True
#         )
#         return

#     await interaction.response.defer()
#     rows, error = query_bigquery(sql, limit=10)

#     if error:
#         await interaction.followup.send(f"❌ Query error: {error}")
#         return

#     if not rows:
#         await interaction.followup.send(
#             "✅ Query executed successfully. No results returned."
#         )
#         return

#     embed = format_results(rows, "Query Results")
#     await interaction.followup.send(embed=embed)


# @bot.tree.command(
#     name="community", description="Get community data for a cryptocurrency."
# )
# async def community(interaction: discord.Interaction, crypto_id: str = "bitcoin"):
#     """Get community data for a cryptocurrency."""
#     project_id = os.getenv("GCP_PROJECT_ID", "discord-bot-484904")
#     dataset_id = os.getenv("BQ_DATASET_ID", "crypto_bot")
#     table_name = os.getenv("BQ_COMMUNITY_TABLE", "community_data")

#     query = f"""
#         SELECT *
#         FROM `{project_id}.{dataset_id}.{table_name}`
#         WHERE crypto_id = '{crypto_id}'
#         ORDER BY timestamp DESC
#     """

#     await interaction.response.defer()
#     rows, error = query_bigquery(query, limit=3)

#     if error:
#         await interaction.followup.send(f"❌ Error querying BigQuery: {error}")
#         return

#     if not rows:
#         await interaction.followup.send(f"No community data found for `{crypto_id}`")
#         return

#     embed = discord.Embed(
#         title=f"👥 {crypto_id.capitalize()} Community Stats",
#         description=f"Latest {len(rows)} record(s)",
#         color=discord.Color.green(),
#     )

#     for row in rows:
#         timestamp = row.get("timestamp", "N/A")
#         reddit_subs = row.get("reddit_subscribers", "N/A")
#         reddit_active = row.get("reddit_accounts_active_48h", "N/A")
#         facebook_likes = row.get("facebook_likes", "N/A")

#         embed.add_field(
#             name=f"⏰ {timestamp}",
#             value=f"**Reddit Subscribers**: {reddit_subs}\n**Active (48h)**: {reddit_active}\n**Facebook Likes**: {facebook_likes}",
#             inline=False,
#         )

#     embed.set_footer(
#         text=f"Data from BigQuery • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     )
#     await interaction.followup.send(embed=embed)


# @bot.tree.command(
#     name="developer", description="Get developer activity data for a cryptocurrency."
# )
# async def developer(interaction: discord.Interaction, crypto_id: str = "bitcoin"):
#     """Get developer activity data for a cryptocurrency."""
#     project_id = os.getenv("GCP_PROJECT_ID", "discord-bot-484904")
#     dataset_id = os.getenv("BQ_DATASET_ID", "crypto_bot")
#     table_name = os.getenv("BQ_DEVELOPER_TABLE", "developer_data")

#     query = f"""
#         SELECT *
#         FROM `{project_id}.{dataset_id}.{table_name}`
#         WHERE crypto_id = '{crypto_id}'
#         ORDER BY timestamp DESC
#     """

#     await interaction.response.defer()
#     rows, error = query_bigquery(query, limit=3)

#     if error:
#         await interaction.followup.send(f"❌ Error querying BigQuery: {error}")
#         return

#     if not rows:
#         await interaction.followup.send(f"No developer data found for `{crypto_id}`")
#         return

#     embed = discord.Embed(
#         title=f"💻 {crypto_id.capitalize()} Developer Activity",
#         description=f"Latest {len(rows)} record(s)",
#         color=discord.Color.purple(),
#     )

#     for row in rows:
#         timestamp = row.get("timestamp", "N/A")
#         stars = row.get("stars", "N/A")
#         forks = row.get("forks", "N/A")
#         commits = row.get("commit_count_4_weeks", "N/A")
#         prs_merged = row.get("pull_requests_merged", "N/A")

#         embed.add_field(
#             name=f"⏰ {timestamp}",
#             value=f"**Stars**: {stars}\n**Forks**: {forks}\n**Commits (4w)**: {commits}\n**PRs Merged**: {prs_merged}",
#             inline=False,
#         )

#     embed.set_footer(
#         text=f"Data from BigQuery • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     )
#     await interaction.followup.send(embed=embed)


# @bot.tree.command(
#     name="list", description="List all available cryptocurrencies in the database."
# )
# async def list_cryptos(interaction: discord.Interaction):
#     """List all available cryptocurrencies in the database."""
#     project_id = os.getenv("GCP_PROJECT_ID", "discord-bot-484904")
#     dataset_id = os.getenv("BQ_DATASET_ID", "crypto_bot")
#     table_name = os.getenv("BQ_MARKET_TABLE", "market_data")

#     query = f"""
#         SELECT DISTINCT crypto_id
#         FROM `{project_id}.{dataset_id}.{table_name}`
#         ORDER BY crypto_id
#     """

#     await interaction.response.defer()
#     rows, error = query_bigquery(query, limit=50)

#     if error:
#         await interaction.followup.send(f"❌ Error querying BigQuery: {error}")
#         return

#     if not rows:
#         await interaction.followup.send("No cryptocurrencies found in the database.")
#         return

#     crypto_list = "\n".join([f"• `{row['crypto_id']}`" for row in rows])

#     embed = discord.Embed(
#         title="🪙 Available Cryptocurrencies",
#         description=crypto_list,
#         color=discord.Color.blue(),
#     )
#     embed.set_footer(text=f"Total: {len(rows)} cryptocurrencies")
#     await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="fng_bar", description="Get the Fear & Greed Index as an emoji bar."
)
async def fng_bar(interaction: discord.Interaction):
    """Fear & Greed Index with Emoji Bar."""
    await interaction.response.defer()
    data, error = crypto_service.fear_and_greed()

    if error:
        await interaction.followup.send(f"❌ Error: {error}")
        return

    val = data.get("value", "50")
    label = data.get("value_classification", "Neutral")
    bar = crypto_service.get_fng_emoji_bar(val)

    embed = discord.Embed(
        title="📈 Crypto Fear & Greed Index",
        description=f"**Value**: `{val}` ({label})\n\n{bar}",
        color=discord.Color.dark_gold(),
    )
    embed.set_footer(text="Data from alternative.me")
    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="fng_gauge", description="Get the Fear & Greed Index as a speedometer image."
)
async def fng_gauge(interaction: discord.Interaction):
    """Fear & Greed Index with Gauge Image."""
    await interaction.response.defer()
    data, error = crypto_service.fear_and_greed()

    if error:
        await interaction.followup.send(f"❌ Error: {error}")
        return

    val = data.get("value", "50")
    label = data.get("value_classification", "Neutral")

    # Create the image
    image_path = crypto_service.create_fng_gauge(val, title=f"Index: {val} ({label})")
    file = discord.File(image_path, filename="fng_gauge.png")

    embed = discord.Embed(
        title="📈 Crypto Fear & Greed Index",
        color=discord.Color.dark_gold(),
    )
    embed.set_image(url="attachment://fng_gauge.png")
    embed.set_footer(text="Data from alternative.me")

    await interaction.followup.send(file=file, embed=embed)


if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        exit(1)

    bot.run(token)
