# GitHub commits, currently only finds a user's commits in the main branch of a GitHub Repository
import requests
from bs4 import BeautifulSoup

import discord
from discord.ext import commands


class GitHubScraper(commands.Cog, name="GitHub Scraper"):
    """Scrapes GitHub repos"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def commitlist(self, context, username, repo_name, organization=""):
        """Finds list of commits on the main branch of a GitHub repo."""  # this is the description that will show up in !help

        if not organization:
            organization = username

        repo_url = f"https://github.com/{organization}/{repo_name}/commits?author={username}"
        commits_list = []  # list of commits in the main branch

        # Finds link of commits on page and continues to older pages of commits until there are no older pages
        while True:
            print("Searching: " + repo_url)
            search_data = requests.get(repo_url)
            search_soup = BeautifulSoup(search_data.text, 'html.parser')

            # finds all the commit links on the page
            links = search_soup.find_all("a", {"class": "Link--primary text-bold js-navigation-open markdown-title"}, href=True)

            # adds links into links_list if they are not already in it
            for link in links:
                full_link = "https://github.com" + link['href']
                if full_link not in commits_list:
                    commits_list.append(full_link)

            # the buttons at the bottom of the page that say "Newer" and "Older"
            page_buttons = search_soup.find_all("a", {"rel": "nofollow", "class": "btn btn-outline BtnGroup-item"})

            # if there are more commits on an older page, then find_links() of that older page
            more_pages = False
            for button in page_buttons:
                if button.get_text() == "Older":
                    more_pages = True
                    repo_url = button['href']

            if not more_pages:
                break

        # writes the commits list to a text file
        with open("list_of_commits.txt", "w") as file:
            file.write(f"{username}'s {len(commits_list)} Commits in Main Branch:\n")
            for commit in commits_list:
                file.write(f"{commit}\n")

        # send text file with list of commits to user
        with open("list_of_commits.txt", "rb") as file:
            await context.reply("Your file is:", file=discord.File(file, "list_of_commits.txt"))


async def setup(bot):
    await bot.add_cog(GitHubScraper(bot))
