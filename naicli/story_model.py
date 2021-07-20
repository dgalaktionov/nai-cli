"""Generated code from story.schema, do not modify manually!"""

from enum import Enum
from typing import Any, List, Optional, TypeVar, Type, cast, Callable
from uuid import UUID


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


class InsertionTypeEnum(Enum):
    newline = "newline"
    sentence = "sentence"
    token = "token"


class TrimDirection(Enum):
    doNotTrim = "doNotTrim"
    trimBottom = "trimBottom"
    trimTop = "trimTop"


class ContextConfig:
    budgetPriority: int
    insertionPosition: int
    insertionType: InsertionTypeEnum
    maximumTrimType: InsertionTypeEnum
    prefix: str
    reservedTokens: int
    suffix: str
    tokenBudget: int
    trimDirection: TrimDirection

    def __init__(self, budgetPriority: int, insertionPosition: int, insertionType: InsertionTypeEnum, maximumTrimType: InsertionTypeEnum, prefix: str, reservedTokens: int, suffix: str, tokenBudget: int, trimDirection: TrimDirection) -> None:
        self.budgetPriority = budgetPriority
        self.insertionPosition = insertionPosition
        self.insertionType = insertionType
        self.maximumTrimType = maximumTrimType
        self.prefix = prefix
        self.reservedTokens = reservedTokens
        self.suffix = suffix
        self.tokenBudget = tokenBudget
        self.trimDirection = trimDirection

    @staticmethod
    def from_dict(obj: Any) -> 'ContextConfig':
        assert isinstance(obj, dict)
        budgetPriority = from_int(obj.get("budgetPriority"))
        insertionPosition = from_int(obj.get("insertionPosition"))
        insertionType = InsertionTypeEnum(obj.get("insertionType"))
        maximumTrimType = InsertionTypeEnum(obj.get("maximumTrimType"))
        prefix = from_str(obj.get("prefix"))
        reservedTokens = from_int(obj.get("reservedTokens"))
        suffix = from_str(obj.get("suffix"))
        tokenBudget = from_int(obj.get("tokenBudget"))
        trimDirection = TrimDirection(obj.get("trimDirection"))
        return ContextConfig(budgetPriority, insertionPosition, insertionType, maximumTrimType, prefix, reservedTokens, suffix, tokenBudget, trimDirection)

    def to_dict(self) -> dict:
        result: dict = {}
        result["budgetPriority"] = from_int(self.budgetPriority)
        result["insertionPosition"] = from_int(self.insertionPosition)
        result["insertionType"] = to_enum(InsertionTypeEnum, self.insertionType)
        result["maximumTrimType"] = to_enum(InsertionTypeEnum, self.maximumTrimType)
        result["prefix"] = from_str(self.prefix)
        result["reservedTokens"] = from_int(self.reservedTokens)
        result["suffix"] = from_str(self.suffix)
        result["tokenBudget"] = from_int(self.tokenBudget)
        result["trimDirection"] = to_enum(TrimDirection, self.trimDirection)
        return result


class Context:
    contextConfig: ContextConfig
    text: str

    def __init__(self, contextConfig: ContextConfig, text: str) -> None:
        self.contextConfig = contextConfig
        self.text = text

    @staticmethod
    def from_dict(obj: Any) -> 'Context':
        assert isinstance(obj, dict)
        contextConfig = ContextConfig.from_dict(obj.get("contextConfig"))
        text = from_str(obj.get("text"))
        return Context(contextConfig, text)

    def to_dict(self) -> dict:
        result: dict = {}
        result["contextConfig"] = to_class(ContextConfig, self.contextConfig)
        result["text"] = from_str(self.text)
        return result


class EphemeralContext:
    contextConfig: ContextConfig
    delay: int
    duration: int
    repeat: bool
    reverse: bool
    startingStep: int
    text: str

    def __init__(self, contextConfig: ContextConfig, delay: int, duration: int, repeat: bool, reverse: bool, startingStep: int, text: str) -> None:
        self.contextConfig = contextConfig
        self.delay = delay
        self.duration = duration
        self.repeat = repeat
        self.reverse = reverse
        self.startingStep = startingStep
        self.text = text

    @staticmethod
    def from_dict(obj: Any) -> 'EphemeralContext':
        assert isinstance(obj, dict)
        contextConfig = ContextConfig.from_dict(obj.get("contextConfig"))
        delay = from_int(obj.get("delay"))
        duration = from_int(obj.get("duration"))
        repeat = from_bool(obj.get("repeat"))
        reverse = from_bool(obj.get("reverse"))
        startingStep = from_int(obj.get("startingStep"))
        text = from_str(obj.get("text"))
        return EphemeralContext(contextConfig, delay, duration, repeat, reverse, startingStep, text)

    def to_dict(self) -> dict:
        result: dict = {}
        result["contextConfig"] = to_class(ContextConfig, self.contextConfig)
        result["delay"] = from_int(self.delay)
        result["duration"] = from_int(self.duration)
        result["repeat"] = from_bool(self.repeat)
        result["reverse"] = from_bool(self.reverse)
        result["startingStep"] = from_int(self.startingStep)
        result["text"] = from_str(self.text)
        return result


class Entry:
    contextConfig: ContextConfig
    displayName: str
    enabled: bool
    forceActivation: bool
    keyRelative: bool
    keys: List[str]
    lastUpdatedAt: int
    nonStoryActivatable: bool
    searchRange: int
    text: str

    def __init__(self, contextConfig: ContextConfig, displayName: str, enabled: bool, forceActivation: bool, keyRelative: bool, keys: List[str], lastUpdatedAt: int, nonStoryActivatable: bool, searchRange: int, text: str) -> None:
        self.contextConfig = contextConfig
        self.displayName = displayName
        self.enabled = enabled
        self.forceActivation = forceActivation
        self.keyRelative = keyRelative
        self.keys = keys
        self.lastUpdatedAt = lastUpdatedAt
        self.nonStoryActivatable = nonStoryActivatable
        self.searchRange = searchRange
        self.text = text

    @staticmethod
    def from_dict(obj: Any) -> 'Entry':
        assert isinstance(obj, dict)
        contextConfig = ContextConfig.from_dict(obj.get("contextConfig"))
        displayName = from_str(obj.get("displayName"))
        enabled = from_bool(obj.get("enabled"))
        forceActivation = from_bool(obj.get("forceActivation"))
        keyRelative = from_bool(obj.get("keyRelative"))
        keys = from_list(from_str, obj.get("keys"))
        lastUpdatedAt = from_int(obj.get("lastUpdatedAt"))
        nonStoryActivatable = from_bool(obj.get("nonStoryActivatable"))
        searchRange = from_int(obj.get("searchRange"))
        text = from_str(obj.get("text"))
        return Entry(contextConfig, displayName, enabled, forceActivation, keyRelative, keys, lastUpdatedAt, nonStoryActivatable, searchRange, text)

    def to_dict(self) -> dict:
        result: dict = {}
        result["contextConfig"] = to_class(ContextConfig, self.contextConfig)
        result["displayName"] = from_str(self.displayName)
        result["enabled"] = from_bool(self.enabled)
        result["forceActivation"] = from_bool(self.forceActivation)
        result["keyRelative"] = from_bool(self.keyRelative)
        result["keys"] = from_list(from_str, self.keys)
        result["lastUpdatedAt"] = from_int(self.lastUpdatedAt)
        result["nonStoryActivatable"] = from_bool(self.nonStoryActivatable)
        result["searchRange"] = from_int(self.searchRange)
        result["text"] = from_str(self.text)
        return result


class LorebookSettings:
    orderByKeyLocations: bool

    def __init__(self, orderByKeyLocations: bool) -> None:
        self.orderByKeyLocations = orderByKeyLocations

    @staticmethod
    def from_dict(obj: Any) -> 'LorebookSettings':
        assert isinstance(obj, dict)
        orderByKeyLocations = from_bool(obj.get("orderByKeyLocations"))
        return LorebookSettings(orderByKeyLocations)

    def to_dict(self) -> dict:
        result: dict = {}
        result["orderByKeyLocations"] = from_bool(self.orderByKeyLocations)
        return result


class Lorebook:
    entries: List[Entry]
    lorebookVersion: int
    settings: LorebookSettings

    def __init__(self, entries: List[Entry], lorebookVersion: int, settings: LorebookSettings) -> None:
        self.entries = entries
        self.lorebookVersion = lorebookVersion
        self.settings = settings

    @staticmethod
    def from_dict(obj: Any) -> 'Lorebook':
        assert isinstance(obj, dict)
        entries = from_list(Entry.from_dict, obj.get("entries"))
        lorebookVersion = from_int(obj.get("lorebookVersion"))
        settings = LorebookSettings.from_dict(obj.get("settings"))
        return Lorebook(entries, lorebookVersion, settings)

    def to_dict(self) -> dict:
        result: dict = {}
        result["entries"] = from_list(lambda x: to_class(Entry, x), self.entries)
        result["lorebookVersion"] = from_int(self.lorebookVersion)
        result["settings"] = to_class(LorebookSettings, self.settings)
        return result


class Parameters:
    badwordsids: List[List[int]]
    maxlength: int
    minlength: int
    prefix: Optional[str]
    repetitionpenalty: float
    repetitionpenaltyrange: int
    repetitionpenaltyslope: float
    tailfreesampling: float
    temperature: float
    topk: int
    topp: float

    def __init__(self, badwordsids: List[List[int]], maxlength: int, minlength: int, prefix: Optional[str], repetitionpenalty: float, repetitionpenaltyrange: int, repetitionpenaltyslope: float, tailfreesampling: float, temperature: float, topk: int, topp: float) -> None:
        self.badwordsids = badwordsids
        self.maxlength = maxlength
        self.minlength = minlength
        self.prefix = prefix
        self.repetitionpenalty = repetitionpenalty
        self.repetitionpenaltyrange = repetitionpenaltyrange
        self.repetitionpenaltyslope = repetitionpenaltyslope
        self.tailfreesampling = tailfreesampling
        self.temperature = temperature
        self.topk = topk
        self.topp = topp

    @staticmethod
    def from_dict(obj: Any) -> 'Parameters':
        assert isinstance(obj, dict)
        badwordsids = from_list(lambda x: from_list(from_int, x), obj.get("bad_words_ids"))
        maxlength = from_int(obj.get("max_length"))
        minlength = from_int(obj.get("min_length"))
        prefix = from_union([from_str, from_none], obj.get("prefix"))
        repetitionpenalty = from_float(obj.get("repetition_penalty"))
        repetitionpenaltyrange = from_int(obj.get("repetition_penalty_range"))
        repetitionpenaltyslope = from_float(obj.get("repetition_penalty_slope"))
        tailfreesampling = from_float(obj.get("tail_free_sampling"))
        temperature = from_float(obj.get("temperature"))
        topk = from_int(obj.get("top_k"))
        topp = from_float(obj.get("top_p"))
        return Parameters(badwordsids, maxlength, minlength, prefix, repetitionpenalty, repetitionpenaltyrange, repetitionpenaltyslope, tailfreesampling, temperature, topk, topp)

    def to_dict(self) -> dict:
        result: dict = {}
        result["bad_words_ids"] = from_list(lambda x: from_list(from_int, x), self.badwordsids)
        result["max_length"] = from_int(self.maxlength)
        result["min_length"] = from_int(self.minlength)
        result["prefix"] = from_union([from_str, from_none], self.prefix)
        result["repetition_penalty"] = to_float(self.repetitionpenalty)
        result["repetition_penalty_range"] = from_int(self.repetitionpenaltyrange)
        result["repetition_penalty_slope"] = to_float(self.repetitionpenaltyslope)
        result["tail_free_sampling"] = to_float(self.tailfreesampling)
        result["temperature"] = to_float(self.temperature)
        result["top_k"] = from_int(self.topk)
        result["top_p"] = to_float(self.topp)
        return result


class ContentSettings:
    banBrackets: bool
    parameters: Parameters
    trimResponses: bool

    def __init__(self, banBrackets: bool, parameters: Parameters, trimResponses: bool) -> None:
        self.banBrackets = banBrackets
        self.parameters = parameters
        self.trimResponses = trimResponses

    @staticmethod
    def from_dict(obj: Any) -> 'ContentSettings':
        assert isinstance(obj, dict)
        banBrackets = from_bool(obj.get("banBrackets"))
        parameters = Parameters.from_dict(obj.get("parameters"))
        trimResponses = from_bool(obj.get("trimResponses"))
        return ContentSettings(banBrackets, parameters, trimResponses)

    def to_dict(self) -> dict:
        result: dict = {}
        result["banBrackets"] = from_bool(self.banBrackets)
        result["parameters"] = to_class(Parameters, self.parameters)
        result["trimResponses"] = from_bool(self.trimResponses)
        return result


class Origin(Enum):
    ai = "ai"
    edit = "edit"
    prompt = "prompt"
    root = "root"
    user = "user"


class Fragment:
    data: str
    origin: Origin

    def __init__(self, data: str, origin: Origin) -> None:
        self.data = data
        self.origin = origin

    @staticmethod
    def from_dict(obj: Any) -> 'Fragment':
        assert isinstance(obj, dict)
        data = from_str(obj.get("data"))
        origin = Origin(obj.get("origin"))
        return Fragment(data, origin)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_str(self.data)
        result["origin"] = to_enum(Origin, self.origin)
        return result


class Datablock:
    chain: bool
    dataFragment: Fragment
    endIndex: int
    fragmentIndex: int
    nextBlock: List[int]
    origin: Origin
    prevBlock: int
    removedFragments: List[Fragment]
    startIndex: int

    def __init__(self, chain: bool, dataFragment: Fragment, endIndex: int, fragmentIndex: int, nextBlock: List[int], origin: Origin, prevBlock: int, removedFragments: List[Fragment], startIndex: int) -> None:
        self.chain = chain
        self.dataFragment = dataFragment
        self.endIndex = endIndex
        self.fragmentIndex = fragmentIndex
        self.nextBlock = nextBlock
        self.origin = origin
        self.prevBlock = prevBlock
        self.removedFragments = removedFragments
        self.startIndex = startIndex

    @staticmethod
    def from_dict(obj: Any) -> 'Datablock':
        assert isinstance(obj, dict)
        chain = from_bool(obj.get("chain"))
        dataFragment = Fragment.from_dict(obj.get("dataFragment"))
        endIndex = from_int(obj.get("endIndex"))
        fragmentIndex = from_int(obj.get("fragmentIndex"))
        nextBlock = from_list(from_int, obj.get("nextBlock"))
        origin = Origin(obj.get("origin"))
        prevBlock = from_int(obj.get("prevBlock"))
        removedFragments = from_list(Fragment.from_dict, obj.get("removedFragments"))
        startIndex = from_int(obj.get("startIndex"))
        return Datablock(chain, dataFragment, endIndex, fragmentIndex, nextBlock, origin, prevBlock, removedFragments, startIndex)

    def to_dict(self) -> dict:
        result: dict = {}
        result["chain"] = from_bool(self.chain)
        result["dataFragment"] = to_class(Fragment, self.dataFragment)
        result["endIndex"] = from_int(self.endIndex)
        result["fragmentIndex"] = from_int(self.fragmentIndex)
        result["nextBlock"] = from_list(from_int, self.nextBlock)
        result["origin"] = to_enum(Origin, self.origin)
        result["prevBlock"] = from_int(self.prevBlock)
        result["removedFragments"] = from_list(lambda x: to_class(Fragment, x), self.removedFragments)
        result["startIndex"] = from_int(self.startIndex)
        return result


class Story:
    currentBlock: int
    datablocks: List[Datablock]
    fragments: List[Fragment]
    step: int
    version: int

    def __init__(self, currentBlock: int, datablocks: List[Datablock], fragments: List[Fragment], step: int, version: int) -> None:
        self.currentBlock = currentBlock
        self.datablocks = datablocks
        self.fragments = fragments
        self.step = step
        self.version = version

    @staticmethod
    def from_dict(obj: Any) -> 'Story':
        assert isinstance(obj, dict)
        currentBlock = from_int(obj.get("currentBlock"))
        datablocks = from_list(Datablock.from_dict, obj.get("datablocks"))
        fragments = from_list(Fragment.from_dict, obj.get("fragments"))
        step = from_int(obj.get("step"))
        version = from_int(obj.get("version"))
        return Story(currentBlock, datablocks, fragments, step, version)

    def to_dict(self) -> dict:
        result: dict = {}
        result["currentBlock"] = from_int(self.currentBlock)
        result["datablocks"] = from_list(lambda x: to_class(Datablock, x), self.datablocks)
        result["fragments"] = from_list(lambda x: to_class(Fragment, x), self.fragments)
        result["step"] = from_int(self.step)
        result["version"] = from_int(self.version)
        return result


class Content:
    context: List[Context]
    ephemeralContext: List[EphemeralContext]
    lorebook: Lorebook
    settings: ContentSettings
    story: Story
    storyContentVersion: int
    storyContextConfig: ContextConfig

    def __init__(self, context: List[Context], ephemeralContext: List[EphemeralContext], lorebook: Lorebook, settings: ContentSettings, story: Story, storyContentVersion: int, storyContextConfig: ContextConfig) -> None:
        self.context = context
        self.ephemeralContext = ephemeralContext
        self.lorebook = lorebook
        self.settings = settings
        self.story = story
        self.storyContentVersion = storyContentVersion
        self.storyContextConfig = storyContextConfig

    @staticmethod
    def from_dict(obj: Any) -> 'Content':
        assert isinstance(obj, dict)
        context = from_list(Context.from_dict, obj.get("context"))
        ephemeralContext = from_list(EphemeralContext.from_dict, obj.get("ephemeralContext"))
        lorebook = Lorebook.from_dict(obj.get("lorebook"))
        settings = ContentSettings.from_dict(obj.get("settings"))
        story = Story.from_dict(obj.get("story"))
        storyContentVersion = from_int(obj.get("storyContentVersion"))
        storyContextConfig = ContextConfig.from_dict(obj.get("storyContextConfig"))
        return Content(context, ephemeralContext, lorebook, settings, story, storyContentVersion, storyContextConfig)

    def to_dict(self) -> dict:
        result: dict = {}
        result["context"] = from_list(lambda x: to_class(Context, x), self.context)
        result["ephemeralContext"] = from_list(lambda x: to_class(EphemeralContext, x), self.ephemeralContext)
        result["lorebook"] = to_class(Lorebook, self.lorebook)
        result["settings"] = to_class(ContentSettings, self.settings)
        result["story"] = to_class(Story, self.story)
        result["storyContentVersion"] = from_int(self.storyContentVersion)
        result["storyContextConfig"] = to_class(ContextConfig, self.storyContextConfig)
        return result


class Metadata:
    createdAt: int
    description: str
    favorite: bool
    id: UUID
    isModified: bool
    lastUpdatedAt: int
    storyMetadataVersion: int
    tags: List[str]
    textPreview: str
    title: str

    def __init__(self, createdAt: int, description: str, favorite: bool, id: UUID, isModified: bool, lastUpdatedAt: int, storyMetadataVersion: int, tags: List[str], textPreview: str, title: str) -> None:
        self.createdAt = createdAt
        self.description = description
        self.favorite = favorite
        self.id = id
        self.isModified = isModified
        self.lastUpdatedAt = lastUpdatedAt
        self.storyMetadataVersion = storyMetadataVersion
        self.tags = tags
        self.textPreview = textPreview
        self.title = title

    @staticmethod
    def from_dict(obj: Any) -> 'Metadata':
        assert isinstance(obj, dict)
        createdAt = from_int(obj.get("createdAt"))
        description = from_str(obj.get("description"))
        favorite = from_bool(obj.get("favorite"))
        id = UUID(obj.get("id"))
        isModified = from_bool(obj.get("isModified"))
        lastUpdatedAt = from_int(obj.get("lastUpdatedAt"))
        storyMetadataVersion = from_int(obj.get("storyMetadataVersion"))
        tags = from_list(from_str, obj.get("tags"))
        textPreview = from_str(obj.get("textPreview"))
        title = from_str(obj.get("title"))
        return Metadata(createdAt, description, favorite, id, isModified, lastUpdatedAt, storyMetadataVersion, tags, textPreview, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["createdAt"] = from_int(self.createdAt)
        result["description"] = from_str(self.description)
        result["favorite"] = from_bool(self.favorite)
        result["id"] = str(self.id)
        result["isModified"] = from_bool(self.isModified)
        result["lastUpdatedAt"] = from_int(self.lastUpdatedAt)
        result["storyMetadataVersion"] = from_int(self.storyMetadataVersion)
        result["tags"] = from_list(from_str, self.tags)
        result["textPreview"] = from_str(self.textPreview)
        result["title"] = from_str(self.title)
        return result


class Book:
    content: Content
    metadata: Metadata
    storyContainerVersion: int

    def __init__(self, content: Content, metadata: Metadata, storyContainerVersion: int) -> None:
        self.content = content
        self.metadata = metadata
        self.storyContainerVersion = storyContainerVersion

    @staticmethod
    def from_dict(obj: Any) -> 'Book':
        assert isinstance(obj, dict)
        content = Content.from_dict(obj.get("content"))
        metadata = Metadata.from_dict(obj.get("metadata"))
        storyContainerVersion = from_int(obj.get("storyContainerVersion"))
        return Book(content, metadata, storyContainerVersion)

    def to_dict(self) -> dict:
        result: dict = {}
        result["content"] = to_class(Content, self.content)
        result["metadata"] = to_class(Metadata, self.metadata)
        result["storyContainerVersion"] = from_int(self.storyContainerVersion)
        return result


def Bookfromdict(s: Any) -> Book:
    return Book.from_dict(s)


def Booktodict(x: Book) -> Any:
    return to_class(Book, x)
