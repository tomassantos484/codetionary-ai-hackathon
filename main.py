import discord
import os
import requests
import json
from dotenv import load_dotenv
from discord.ext import commands
from discord import Embed

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
APP_ID = os.getenv('APP_ID')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
OPENROUTER_KEY = os.getenv('OPENROUTER_API_KEY')

client = commands.Bot(command_prefix = '!', intents=discord.Intents.all())

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Learning Computer Science!"))
    try:
        synced = await client.tree.sync()
    except Exception as e:
        print(e)

    print("We are ready to learn!")

@client.tree.command(name="roadmap", description="Generate a personalized learning roadmap based on user's career path, school, year, etc.")
async def roadmap(interaction: discord.Interaction, name: str, career_path: str, school: str, year: str, location: str, interests: str):
    await interaction.response.defer(ephemeral=False)

    def get_response(model, query):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                json={"model": model, "messages": [{"role": "user", "content": query}]}
            )
            response.raise_for_status()  # This will raise an exception for HTTP errors
            return response.json()
        except requests.RequestException as e:
            print(f"API call failed: {e}")
            return None

    query = (f"Introduce yourself to the user as Codetionary and generate a personalized roadmap/timeline for {name} who is interested in {career_path} "
             f"at {school} in {year}, located in {location}, with interests in {interests}. "
             "Outline steps the user should take to achieve their goals, in bullet points, "
             "making it as personal as possible.")
    response = get_response("gryphe/mythomist-7b:free", query)

    if response and 'choices' in response and response['choices']:
        statement = response['choices'][0]['message']['content']
        # Consider the character limit when sending the message
        if len(statement) <= 2000:
            await interaction.followup.send(statement, ephemeral=False)
        else:
            # If the statement is too long, use an embed or split the message
            embed = Embed(title="Your Learning Roadmap", description="Here's your personalized learning roadmap:")
            chunks = [statement[i:i+1500] for i in range(0, len(statement), 1500)]
            for i, chunk in enumerate(chunks, start=1):
                embed.add_field(name=f"Part {i}", value=chunk, inline=False)
            await interaction.followup.send(embed=embed)
    else:
        error_message = "Sorry, I couldn't generate a roadmap. Please try again later!"
        await interaction.followup.send(error_message, ephemeral=False)

# Second command => Topics & Concepts
@client.tree.command(name="learn", description="Learn about a specific topic")
async def learn(interaction: discord.Interaction, topic: str):
     # Immediately defer the interaction to indicate processing is happening
    # and to get more time for sending the response.
    await interaction.response.defer(ephemeral=False)

    def getResponse(model, query):
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
            },
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": query}],
            })
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API call failed with status code {response.status_code}")
            return None
        
    query = f"For the following Computer Science topic, explain it to the user in the most concise way possible, in a way that they would understand the best: {topic}."
    response = getResponse("gryphe/mythomist-7b:free", query)
    if response and 'choices' in response and len(response['choices']) > 0:
        # Access and send the statement
        statement = response['choices'][0]['message']['content']
        await interaction.followup.send(statement, ephemeral=False)
    else:
        # Handle error or empty response
        error_message = "Sorry, I couldn't fetch a random statement. Please try again later!"
        await interaction.followup.send(error_message, ephemeral=False)
    
# Fourth command => Code Examples
@client.tree.command(name="code", description="Get code examples for a specific topic")
async def code(interaction: discord.Interaction, topic: str, language: str):
    await interaction.response.defer(ephemeral=False)

    def get_response(model, query):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                json={"model": model, "messages": [{"role": "user", "content": query}]}
            )
            response.raise_for_status()  # This will raise an exception for HTTP errors
            return response.json()
        except requests.RequestException as e:
            print(f"API call failed: {e}")
            return None

    query = (f"Introduce yourself to the user as Codetionary and provide code examples for the following Computer Science topic and language, being as specific and precise as possible to assist the user in learning how to code and their understanding of it: {topic} in {language}.")
    response = get_response("gryphe/mythomist-7b:free", query)

    if response and 'choices' in response and response['choices']:
        statement = response['choices'][0]['message']['content']
        # Consider the character limit when sending the message
        if len(statement) <= 2000:
            await interaction.followup.send(statement, ephemeral=False)
        else:
            # If the statement is too long, use an embed or split the message
            embed = Embed(title="Code Examples", description="Here are some code examples for the topic:")
            chunks = [statement[i:i+1500] for i in range(0, len(statement), 1500)]
            for i, chunk in enumerate(chunks, start=1):
                embed.add_field(name=f"Part {i}", value=chunk, inline=False)
            await interaction.followup.send(embed=embed)
    else:
        error_message = "Sorry, I couldn't fetch code examples. Please try again later!"
        await interaction.followup.send(error_message, ephemeral=False)


#Fifth command => ping
@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)}ms", ephemeral=True) 


client.run(DISCORD_TOKEN)