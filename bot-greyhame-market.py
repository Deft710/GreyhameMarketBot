import discord
import json
import re
import os
from discord.ext import commands

# Replace with your actual bot token and category IDs
TOKEN = ('BOTTOKENHERE-Deft')  # Ensure you keep this token secure.
CATEGORY_ID = PUTCATAGORYHERE  # The category ID for ticket channels
TRANSCRIPT_CATEGORY_ID = PUTTRANSCRIPTCATAGORYHERE  # The category ID for the transcript channel

# Define the bot with the appropriate intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load prices from prices.json
def load_prices():
    try:
        with open("prices.json", "r") as file:
            price_list = json.load(file)
            
            # Normalize all the keys to lowercase for case-insensitive access
            # Remove underscores for easier comparison
            return {key.lower().replace("_", " "): value for key, value in price_list.items()}
    except FileNotFoundError:
        print("prices.json file not found.")
        return {}

# Command to display prices with pagination
@bot.command()
async def prices(ctx, page: int = 1):
    price_list = load_prices()
    items_per_page = 10
    chunks = chunk_price_list(price_list, chunk_size=items_per_page)
    total_pages = len(chunks)
    
    if page < 1 or page > total_pages:
        await ctx.send(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
        return

    page_data = chunks[page - 1]
    message = "\n".join(page_data)
    await ctx.send(f"**Market Prices (Page {page}/{total_pages})**:\n{message}")

# Helper function to split the list into chunks
def chunk_price_list(price_list, chunk_size=10):
    price_items = [f"{item.title()}: ${price}" for item, price in price_list.items()]
    return [price_items[i:i + chunk_size] for i in range(0, len(price_items), chunk_size)]

@bot.command()
async def order(ctx, *, args):
    """Order items in the format 'item quantity, item quantity'."""
    price_list = load_prices()
    order_summary = []
    total_cost = 0
    items = args.split(',')
    
    for item in items:
        try:
            item_name, quantity = item.strip().split()
            quantity = int(quantity)

            # Normalize item name to lowercase and replace underscores for easy comparison
            normalized_item_name = item_name.lower().replace("_", " ")

            # Check if the normalized item name exists in the price list
            if normalized_item_name in price_list:
                cost = price_list[normalized_item_name] * quantity
                total_cost += cost
                order_summary.append(f"{quantity}x {item_name.replace('_', ' ').title()} - ${cost}")
            else:
                await ctx.send(f"Sorry, {item_name} is not available for sale. Available items: {', '.join(price_list.keys())}")
                return
        except ValueError:
            await ctx.send(f"Invalid order format for '{item.strip()}', use 'item_name quantity'.")
            return

    # Create a ticket for the order
    category = discord.utils.get(ctx.guild.categories, id=CATEGORY_ID)
    if category:
        channel = await category.create_text_channel(f"ticket-{ctx.author.name}")
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await channel.set_permissions(ctx.author, view_channel=True, send_messages=True)
        await channel.send(f"Hello {ctx.author.mention}, your order summary:\n"
                           f"**Order Summary**:\n" + "\n".join(order_summary) + f"\n**Total Cost**: ${total_cost}")
        await ctx.send(f"Your order has been placed and a ticket has been created: {channel.mention}")
    else:
        await ctx.send("Ticket category not found!")

@bot.command()
async def calc(ctx, *, expression):
    """Calculate the total cost of items based on the price and quantity."""
    price_list = load_prices()
    try:
        item_name, quantity = expression.split()
        quantity = int(quantity)

        # Normalize item name to lowercase and replace underscores for easy comparison
        normalized_item_name = item_name.lower().replace("_", " ")

        # Check if the normalized item name exists in the price list
        if normalized_item_name in price_list:
            total_cost = price_list[normalized_item_name] * quantity
            await ctx.send(f"The total cost for {quantity}x {item_name.replace('_', ' ').title()} is: ${total_cost}")
        else:
            await ctx.send(f"Sorry, {item_name} is not available for sale. Available items: {', '.join(price_list.keys())}")
    except ValueError:
        await ctx.send("Please provide the item and quantity in the format: `!calc <item_name> <quantity>`.")

@bot.command()
@commands.has_permissions(administrator=True)
async def close(ctx):
    """Close the ticket and send a transcript of the channel."""
    # Get the last 1000 messages from the channel
    messages = []
    async for message in ctx.channel.history(limit=1000):
        messages.append(f"{message.author}: {message.content}")

    # Create the transcript content
    transcript_content = "\n".join(messages)

    # Save transcript as a .txt file
    transcript_filename = f"transcript-{ctx.channel.name}.txt"
    with open(transcript_filename, "w") as f:
        f.write(transcript_content)

    # Send the transcript file to the transcript channel
    transcript_category = discord.utils.get(ctx.guild.categories, id=TRANSCRIPT_CATEGORY_ID)
    if transcript_category:
        # Create a new channel for the transcript
        transcript_channel = await transcript_category.create_text_channel(f"transcript-{ctx.channel.name}")
        
        # Send the transcript file to the transcript channel
        with open(transcript_filename, "rb") as f:
            await transcript_channel.send("**Transcript**", file=discord.File(f, transcript_filename))

        # Delete the current channel after sending the transcript
        await ctx.channel.delete()

        await ctx.send(f"Ticket closed. The transcript has been saved to: {transcript_channel.mention}")
    else:
        await ctx.send("Transcript category not found!")

# New commands added:

@bot.command()
async def test(ctx):
    """Test the bot's response."""
    await ctx.send("Pong! The bot is working okay.")

@bot.command()
async def credits(ctx):
    """Display bot credits."""
    await ctx.send("Made by Deft710")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Run the bot with the provided token
bot.run('BOTTOKENHERE-Deft')