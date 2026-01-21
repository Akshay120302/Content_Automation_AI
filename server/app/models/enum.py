from enum import Enum

class PlatformEnum(str, Enum):
    youtube = "youtube"
    reddit = "reddit"
    instagram = "instagram"
    linkedin = "linkedin"
    medium = "medium"
    twitter = "twitter"
    facebook = "facebook"
    pinterest = "pinterest"


class ContentTypeEnum(str, Enum):
    text = "text"
    video = "video"
    audio = "audio"
    image = "image"
    any = "any"


class AgentModelEnum(str, Enum):
    gpt_4 = "gpt-4"
    gpt_35 = "gpt-3.5-turbo"
    claude_opus = "claude-3-opus"
    claude_sonnet = "claude-3-sonnet"
    gemini_pro = "gemini-pro"
    llama3 = "llama3"


class FrequencyEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class TimezoneEnum(str, Enum):
    IST = "IST"
    PST = "PST"
    EST = "EST"
    GMT = "GMT"
    CST = "CST"
    JST = "JST"
    AEST = "AEST"


class GenreEnum(str, Enum):
    all = "all"
    tech = "tech"
    business = "business"
    entertainment = "entertainment"
    education = "education"
    health_fitness = "health_fitness"
    gaming = "gaming"
    news = "news"
    comedy = "comedy"
    science = "science"


class TopicTypeEnum(str, Enum):
    trending = "trending"
    day = "topic_of_the_day"
    region = "topic_of_the_region"
    specific = "specific"
