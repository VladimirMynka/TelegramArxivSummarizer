from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_URL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_URL)


async def summarize_article(article, references_summaries=None):
    prompt = f"\n\n{article['text']}\n\n"

    if references_summaries:
        prompt += "Включи следующие резюме ссылок для улучшенной суммаризации:\n"
        for ref in references_summaries:
            prompt += f"- {ref}\n"

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Здарова братан! Общайся со мной на равных, я шарю за все эти эмбеддинги и прочие штуки которыми ты манипулируешь, так что feel free. Можешь по-братски набросать выжимку из этой статьи, так, чтобы влезло в средний пост в телеграмме. Распиши, что за проблемы авторы ставят, что они такого там наделали нового, что позволило им обогнать всех конкурентов в этой области. Расскажи, с кем сравнивались и что они итого считают своим вкладом в эту область. Напиши, что авторы считают своим главным достижением в этой статье. Не бойся нецензурных слов, если чувствуешь, что статья говно говна, то так и пиши, не стесняйся. Не пиши ничего, кроме своего охрененного саммери. Не используй заголовки маркдауна, если хочешь сделать заголовок - пиши его в звёздочках. Всё, давай, погнали!",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    summary = response.choices[0].message.content.strip()
    return summary
