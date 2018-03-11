from textblob import TextBlob

analysis = TextBlob("TextBlob sure looks like it has some nice features!")

print(analysis.translate(to='es'))
print(analysis.tags)
print(analysis.sentiment)