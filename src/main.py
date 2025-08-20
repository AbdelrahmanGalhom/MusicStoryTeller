from services.langchain_service import LangChainService

serv = LangChainService()

print(serv.generate_story_from_song_name("The hudson", "The favors"))