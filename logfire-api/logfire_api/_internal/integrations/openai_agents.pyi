import contextvars
from _typeshed import Incomplete
from abc import abstractmethod
from agents import Span, SpanData, Trace
from agents.tracing import ResponseSpanData
from agents.tracing.setup import TraceProvider
from agents.tracing.spans import SpanError, TSpanData
from dataclasses import dataclass
from logfire import Logfire as Logfire, LogfireSpan as LogfireSpan
from logfire._internal.formatter import logfire_format as logfire_format
from logfire._internal.scrubbing import NOOP_SCRUBBER as NOOP_SCRUBBER
from logfire._internal.utils import handle_internal_errors as handle_internal_errors, log_internal_error as log_internal_error, truncate_string as truncate_string
from openai.types.responses import Response
from types import TracebackType
from typing import Any, Generic, TypeVar
from typing_extensions import Self

class LogfireTraceProviderWrapper:
    wrapped: Incomplete
    logfire_instance: Incomplete
    def __init__(self, wrapped: TraceProvider, logfire_instance: Logfire) -> None: ...
    def create_trace(self, name: str, trace_id: str | None = None, disabled: bool = False, **kwargs: Any) -> Trace: ...
    def create_span(self, span_data: TSpanData, span_id: str | None = None, parent: Trace | Span[Any] | None = None, disabled: bool = False) -> Span[TSpanData]: ...
    def __getattr__(self, item: Any) -> Any: ...
    @classmethod
    def install(cls, logfire_instance: Logfire) -> None: ...

@dataclass
class LogfireSpanHelper:
    span: LogfireSpan
    parent: Trace | Span[Any] | None = ...
    def start(self, mark_as_current: bool): ...
    def end(self, reset_current: bool): ...
    def maybe_detach(self, reset_current: bool): ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType): ...
T = TypeVar('T', Trace, Span[TSpanData])

@dataclass
class LogfireWrapperBase(Generic[T]):
    wrapped: T
    span_helper: LogfireSpanHelper
    token: contextvars.Token[T | None] | None = ...
    def start(self, mark_as_current: bool = False): ...
    def finish(self, reset_current: bool = False): ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType): ...
    @abstractmethod
    def on_ending(self): ...
    @abstractmethod
    def attach(self): ...
    @abstractmethod
    def detach(self): ...
    def __getattr__(self, item: str): ...

@dataclass
class LogfireTraceWrapper(LogfireWrapperBase[Trace], Trace):
    def on_ending(self) -> None: ...
    token = ...
    def attach(self) -> None: ...
    def detach(self) -> None: ...
    @property
    def trace_id(self) -> str: ...
    @property
    def name(self) -> str: ...
    def export(self) -> dict[str, Any] | None: ...

@dataclass
class LogfireSpanWrapper(LogfireWrapperBase[Span[TSpanData]], Span[TSpanData]):
    token = ...
    def attach(self) -> None: ...
    def detach(self) -> None: ...
    def on_ending(self) -> None: ...
    @property
    def trace_id(self) -> str: ...
    @property
    def span_id(self) -> str: ...
    @property
    def span_data(self) -> SpanData: ...
    @property
    def parent_id(self) -> str | None: ...
    def set_error(self, error: SpanError) -> None: ...
    @property
    def error(self) -> SpanError | None: ...
    def export(self) -> dict[str, Any] | None: ...
    @property
    def started_at(self) -> str | None: ...
    @property
    def ended_at(self) -> str | None: ...

def attributes_from_span_data(span_data: SpanData, msg_template: str) -> dict[str, Any]: ...
def get_basic_response_attributes(response: Response): ...
def get_magic_response_attributes() -> dict[str, Any]: ...
def get_response_span_events(span: ResponseSpanData): ...
def input_to_events(inp: dict[str, Any]): ...
def unknown_event(inp: dict[str, Any]): ...
