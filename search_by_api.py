from serpapi import GoogleSearch

params = {
  "api_key": "3999fd790801bc6e48e53a4aef4e832d75cc6c4bc9af01db6506ebc63c4676de",
  "engine": "google",
  "q": "who is Jay Chou?",
  "location": "Austin, Texas, United States",
  "google_domain": "google.com",
  "gl": "us",
  "hl": "en"
}

search = GoogleSearch(params)
results = search.get_dict()
print(results)