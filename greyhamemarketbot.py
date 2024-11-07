import discord
from discord.ext import commands
import asyncio

# Your bot token (replace with your actual token)
TOKEN = ('hereyourtoken')

CATEGORY_ID = hereyourcatagoryid  # The category ID for the ticket channels
TRANSCRIPTS_CATEGORY_ID = hereyourcatagoryid  # The category ID for transcript channels

# Define the bot with the appropriate intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Market items and prices (as an example)
price_list = {
    'diamond_sword': 1000,  
    'maxed_diamond_set': 10000,
    'advocaat': 20, 'bright_green_absinthe': 22, 'calvados': 30, 'fine_beer': 16,
    'fine_darkbeer': 16, 'fine_wheatbeer': 16, 'glowing_mushroom_vodka': 20, 'golden_mead': 18,
    'golden_rum': 20, 'great_apple_cider': 32, 'old_tom_gin': 26, 'potato_soup': 17, 
    'red_wine': 18, 'russian_vodka': 19, 'scotch_whiskey': 20, 'strong_absinthe': 21, 
    'strong_coffee': 18, 'sweet_golden_apple_mead': 21, 'tequila_anejo': 19,
    'baileys': 22, 'blazing_whiskey': 32, 'brandy': 22, 'crimson_wine': 26, 
    'decay_absinthe': 28, 'ender_beer': 26, 'essential_oils': 27, 'kombucha': 25, 
    'hot_chocolate': 22, 'old_jenever': 23, 'premium_saké': 25, 'strong_tea': 22,
    'chai_blossom': 32, 'crystal_lemonade_slushie': 33, 'strawberry_rose_agua_fresca': 34, 
    'sparkling_honey_limeade': 32, 'mango_dragonfruit_refresher': 30, 'blue_mojito': 33, 
    'coconut_milk': 33, 'espresso': 22, 'maple_syrup': 34, 'dark_rum': 36, 'white_rum': 32, 
    'summer_berry_cocktail': 42, 'pineapple_peach_agua_fresca': 46, 'cosmopolitan': 44, 
    'peach_blueberry_sangria_mocktail': 34, 'strawberry_banana_smoothie': 39
}

# Function to split the list into chunks
def chunk_price_list(price_list, chunk_size=10):
    """Splits the price list into smaller chunks."""
    price_items = [f"{item.replace('_', ' ').title()}: ${price}" for item, price in price_list.items()]
    return [price_items[i:i + chunk_size] for i in range(0, len(price_items), chunk_size)]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def prices(ctx, page: int = 1):
    """Displays the list of available items with prices in multiple parts."""
    # Split the price list into chunks of 10 items per message
    chunks = chunk_price_list(price_list, chunk_size=10)
    
    total_pages = len(chunks)
    if total_pages > 4:
        total_pages = 4  # Limit to 4 pages

    # Validate page number
    if page < 1 or page > total_pages:
        await ctx.send(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
        return

    # Get the corresponding page
    page_data = chunks[page - 1]
    message = "\n".join(page_data)

    # Send the message for the selected page
    await ctx.send(f"**Market Prices (Page {page}/{total_pages})**:\n{message}")

@bot.command()
async def order(ctx, *, args):
    """Order items in the format 'item quantity, item quantity'."""
    order_summary = []
    total_cost = 0
    items = args.split(',')
    
    for item in items:
        try:
            item_name, quantity = item.strip().split()
            quantity = int(quantity)
            
            if item_name in price_list:
                cost = price_list[item_name] * quantity
                total_cost += cost
                order_summary.append(f"{quantity}x {item_name.replace('_', ' ').title()} - ${cost}")
            else:
                await ctx.send(f"Sorry, {item_name} is not on the menu.")
                return
        except ValueError:
            await ctx.send(f"Invalid order format for '{item.strip()}', please use 'item_name quantity'.")
            return

    # Create a ticket for the order
    category = discord.utils.get(ctx.guild.categories, id=CATEGORY_ID)
    if category:
        # Create a new ticket channel
        channel = await category.create_text_channel(f"ticket-{ctx.author.name}")
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await channel.set_permissions(ctx.author, view_channel=True, send_messages=True)
        
        # Send order summary in the ticket channel
        await channel.send(f"Hello {ctx.author.mention}, your order summary:\n"
                           f"**Order Summary**:\n" + "\n".join(order_summary) + f"\n**Total Cost**: ${total_cost}")
        await ctx.send(f"Your order has been placed and a ticket has been created: {channel.mention}")
    else:
        await ctx.send("Ticket category not found!")

@bot.command()
async def close(ctx):
    """Close a ticket channel."""
    # Ensure only admins or ticket owner can close the ticket
    if ctx.author.permissions_in(ctx.channel).administrator or ctx.channel.name.startswith(f"ticket-{ctx.author.name}"):
        await ctx.channel.delete()
        await ctx.send("Your ticket has been closed.")
    else:
        await ctx.send("You do not have permission to close this ticket.")

@bot.command()
async def transcript(ctx):
    """Creates a transcript of the ticket and moves it to a designated category."""
    # Check if the channel is a ticket channel
    if ctx.channel.name.startswith("ticket-"):
        category = discord.utils.get(ctx.guild.categories, id=TRANSCRIPTS_CATEGORY_ID)
        if category:
            # Create the transcript (a simple message log of the channel)
            messages = await ctx.channel.history(limit=100).flatten()
            transcript_content = "\n".join([f"{msg.author}: {msg.content}" for msg in messages])

            # Create a new channel in the transcripts category
            transcript_channel = await category.create_text_channel(f"transcript-{ctx.channel.name}")
            await transcript_channel.send(f"**Transcript for {ctx.channel.name}**\n{transcript_content}")
            
            # Optionally, delete the ticket after creating the transcript
            await ctx.channel.delete()
            await ctx.send(f"Transcript created and the ticket has been closed.")
        else:
            await ctx.send("Transcript category not found!")
    else:
        await ctx.send("This command can only be used in a ticket channel.")

@bot.command()
async def credits(ctx):
    """Displays the credits for the bot."""
    await ctx.send("This bot was made by Deft710.")

# Run the bot with the provided token
bot.run(TOKEN)