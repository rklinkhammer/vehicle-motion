# Future dmotor adapter contract

No adapter or daemon connection is present in this milestone. Use the installed
Linux C++14 package when integration is approved:

```cmake
find_package(dmotorClient CONFIG REQUIRED)
target_link_libraries(vehicle_executor PRIVATE dmotor::client)
```

Include only the public `dmotor_sw/client.hpp`. No Runtime, KernelDevice, UIO,
service_protocol.hpp, packet serialization or direct socket implementation here.
The target SDK needs dmotor-client-dev and dmotor-client-staticdev for its own
architecture; a native archive is not an ARM archive.

One serialized event-loop caller owns Client. Construction performs admission ping
and takes the sole-client slot, even for status-only use. No independent heartbeat
thread may hide a stalled executor. Current recommended idle ping is 100 ms and
lease 500 ms; request waits default to 250 ms, prepare 2000 ms. These are existing
client budgets, not approved autonomy deadlines or real-time guarantees.

Only status() replies supply measured_mrpm and position_counts. Telemetry lacks
full fault/validity/reset metadata: do not fabricate it or interpret zero fields
on other replies as observations. Missing metadata blocks a production feedback
contract until supported upstream or conservatively handled by reviewed policy.

`okay` acknowledges handler completion, not motor application or safe stopping.
Rejection returns okay=false and daemon attempts HALT. ClientError closes the
connection and leaves outcome potentially unknown: no automatic replay/reconnect.
Local validation exceptions do not send a command. An applied sequence is not a
goal-completion measurement. Explicit quit()/halt() acknowledgment must be checked;
destructor/disconnect cannot confirm HALT or physical stopping.

prepare() is PL-only. recovery_status() currently reports unavailable and
admission_open=false. Older daemons reject the schema-2 query and disconnect; do
not fall back to assumed admission. STOP/disable requires global rearm. A future
adapter must refuse normal motion without the reviewed admission contract; never
substitute prepare, healthy heartbeat or enable bits for completed live recovery.

Controlled velocity STOP, channel disable and global HALT are distinct. Disable
can brake and is not global coast; HALT requests global coast through the monitor
gate. Keep those meanings in dmotor, without reimplementing protection here.
