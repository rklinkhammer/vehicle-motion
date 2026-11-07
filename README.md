# vehicle-motion

Autonomous vehicle motion architecture and offline simulation. Created 2026-11-06.
No hardware connection, normal motion executor, navigation stack or live recovery
is implemented here. Hardware testing is paused pending assembled monitor and
motor boards. dmotor retains its commissioning-first release scope.

Start with [architecture](docs/architecture.md), [decisions and open questions](docs/decisions.md),
[simulation scope](docs/simulation.md) and the [client integration contract](docs/dmotor_boundary.md).

Run from this directory with Python 3.9+ (standard library only):

```sh
python3 -m simulation.demo
python3 -m unittest discover -s tests -v
```

The demo advances a fake clock, commands fictional left/right wheel speeds, then
models deceleration. Its wheel command is a plant input, not an autonomous goal or
a daemon API. Values cannot be used as physical vehicle acceptance evidence.
