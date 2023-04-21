from crossword import *

word_list = [
    "abundant", "adorable", "adventure", "affection", "agreeable", "amazing", "ambitious", "angelic", "appealing", "artistic",
    "astonishing", "attractive", "authentic", "awesome", "balanced", "beautiful", "beloved", "beneficial", "blissful", "bold",
    "brave", "bright", "brilliant", "buoyant", "calm", "captivating", "carefree", "charming", "cheerful", "cherished",
    "classic", "clever", "colorful", "comfortable", "compassionate", "confident", "considerate", "content", "convenient", "cozy",
    "creative", "cuddly", "cultivated", "cute", "daring", "dazzling", "delicate", "delightful", "dependable", "desirable",
    "determined", "devoted", "dignified", "divine", "dreamy", "durable", "eager", "earnest", "easygoing", "elegant",
    "eloquent", "embraceable", "emotional", "enchanting", "endearing", "energetic", "enthusiastic", "essential", "eternal", "exciting",
    "exquisite", "extraordinary", "fabulous", "fair", "faithful", "fantastic", "fascinating", "flawless", "fortunate", "free",
    "friendly", "funny", "generous", "gentle", "genuine", "glamorous", "gleeful", "glorious", "good", "gorgeous",
    "graceful", "gracious", "grand", "great", "happy", "harmonious", "healing", "healthy", "heartfelt", "heavenly",
    "helpful", "honest", "hopeful", "humble", "humorous", "ideal", "imaginative", "immaculate", "immortal", "impartial",
    "important", "impressive", "incredible", "innocent", "insightful", "inspirational", "intelligent", "intense", "intimate", "intriguing",
    "inviting", "irresistible", "joyful", "joyous", "jubilant", "keen", "kind", "kindhearted", "lively", "lovable",
    "lovely", "loyal", "luminous", "magical", "magnificent", "marvelous", "mature", "meaningful", "memorable", "meticulous",
    "mighty", "miraculous", "modern", "modest", "mystical", "natural", "neat", "nice", "noble", "nostalgic",
    "novel", "nurturing", "optimistic", "outgoing", "outstanding", "passionate", "patient", "peaceful", "perfect", "playful",
    "pleased", "pleasant", "pleasurable", "poised", "polished", "positive", "powerful", "precious", "pretty", "priceless",
    "principled", "productive", "professional", "profound", "promising", "proud", "pure", "purposeful", "radiant"
]

cac = crossword(30, 100, word_list, [0 for word in word_list])
for row in cac.answer:
    print(''.join(row))