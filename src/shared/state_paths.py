"""Safe resolution of runtime state paths (audit chain, ledgers, stores).

Fas 3.15 (adversarial finding). The paths to every persistent artifact the
agent's accountability rests on come from environment variables and are opened
by name. Two things follow, and both were demonstrated on the real signed
bundle:

  * A pre-planted SYMLINK at the state path is followed. The audit trail can be
    redirected into any file the process can write - out of the volume that is
    backed up and monitored, or on top of a file the operator relies on. The
    attacker does not need to set the variable; they need to create one link
    inside a shared volume, which a sidecar, a restore or an earlier foothold
    can do.
  * ".." in the variable walks out of the state directory, so the "all state is
    confined to /app/state" posture the image and the k8s manifest assert was
    an assertion, not a guarantee.

TWO GUARDS, BECAUSE ONE IS NOT ENOUGH
  1. O_NOFOLLOW on the final component: opening a state file that IS a symlink
     fails, always, regardless of where it points. This is the guard that does
     not depend on configuration.
  2. Containment under DOER_STATE_ROOT when it is set (the emitted image and
     manifest set it to the state volume): the realpath of the state file must
     lie inside the realpath of the root. This is what closes ".." and a
     symlinked PARENT directory, which O_NOFOLLOW cannot see.

FAIL-CLOSED, AND THE POSTURE IS DISCLOSED
A refused state path raises StatePathRefused, and the callers already treat an
unusable ledger as "do not release" and an unusable audit chain as "do not
proceed". state_confinement() reports confined:<root> or unconfined so a
deployment that has not bound a root is visible rather than assumed safe.
"""
import errno
import os
from typing import Optional

ENV_STATE_ROOT = "DOER_STATE_ROOT"


class StatePathRefused(RuntimeError):
    """A state path is unsafe to use. Never downgrade this to a warning."""


def _configured_root() -> str:
    """The raw DOER_STATE_ROOT value, stripped. Empty means unbound."""
    return os.environ.get(ENV_STATE_ROOT, "").strip()


def state_root() -> Optional[str]:
    """The directory all state must live inside, or None when unbound."""
    root = _configured_root()
    if not root:
        return None
    try:
        return os.path.realpath(root)
    except OSError:
        return None


def state_confinement() -> str:
    """Disclosed, never assumed: confined:<root> or unconfined."""
    root = state_root()
    return ("confined:" + root) if root else "unconfined"


def assert_contained(path: str) -> str:
    """Return path, or raise if a bound state root does not contain it.

    Compared on REALPATH, so a symlinked parent directory cannot be used to
    step outside, and ".." is normalised away before the comparison rather than
    pattern-matched out of the string.
    """
    root = state_root()
    if root is None:
        return path
    target = os.path.realpath(path)
    if target == root or target.startswith(root + os.sep):
        return path
    raise StatePathRefused(
        "state path %r resolves to %r, which is outside the bound state root %r"
        % (path, target, root))


def ensure_parent(path: str) -> None:
    """Create the containing directory, after the containment check."""
    assert_contained(path)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def open_state_fd(path: str, flags: int, mode: int = 0o600) -> int:
    """os.open with O_NOFOLLOW and containment enforced.

    O_NOFOLLOW applies to the FINAL component only - that is the documented
    POSIX behaviour, and the reason assert_contained() exists beside it rather
    than instead of it.
    """
    assert_contained(path)
    try:
        return os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), mode)
    except OSError as e:
        if e.errno in (errno.ELOOP, errno.EMLINK):
            raise StatePathRefused(
                "state path %r is a symlink; refusing to write the agent's own state through it"
                % path)
        raise


def open_state(path: str, mode: str = "r", encoding: Optional[str] = "utf-8"):
    """A text handle on a state file that is neither a symlink nor out of root."""
    if mode in ("r", "rt"):
        flags = os.O_RDONLY
    elif mode in ("w", "wt"):
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    elif mode in ("a", "at"):
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    elif mode in ("a+", "r+"):
        flags = os.O_RDWR | os.O_CREAT
    else:
        raise ValueError("unsupported state file mode: %r" % mode)
    fd = open_state_fd(path, flags)
    try:
        return os.fdopen(fd, mode if "b" in mode else (mode + ""), encoding=encoding)
    except Exception:
        os.close(fd)
        raise
