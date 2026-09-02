from twitch_auto_clipper_sqrtminusone.clip.Clip import Clip

from collections.abc import Callable
from typing import TypeAlias

OnClipCallBack: TypeAlias = Callable[[Clip], None]
