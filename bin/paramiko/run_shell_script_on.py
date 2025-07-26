from common import *
from datetime import date
import asyncio
import time

# Run local script or script content on remote machine over ssh channel.

CHECK_SEQ = """
awk -F, '
BEGIN {
    flag = 1
}

{
    if (NR == 1) next;

    if (prev_val ~ /^-?[0-9]+(\\.[0-9]+)?$/) {
        cur_val = $(NF) + 0
        if (cur_val != prev_val + 1) {
            print "Line " NR " not continuous, prev:" prev_val ", cur:" cur_val
            flag = 0
            exit 2
        }
        prev_val = cur_val
    } else {
        prev_val = $(NF) + 0
        next
    }
}

END {
    print flag ? "passed" : "failed"
}
' $1
"""


class RemoteScriptRunner(object):
    SCRIPT_PATH = ".paramiko"

    def __init__(self, conn: SSHConnection, name: str, content: str=""):
        conn._ensure_remote_path(self.SCRIPT_PATH)
        self._conn = conn
        self._name = name
        if content:
            self.write_script(content)
        else:
            self.write_script(self.load_local_script(name))

    @property
    def name(self):
        if self._name.endswith('.sh'):
            return self._name
        return self._name + '.sh'

    @property
    def path(self):
        return "~/%s/%s" % (self.SCRIPT_PATH, self.name)

    def load_local_script(self, script_name: str):
        fpath = os.path.join("shell_scripts", script_name)
        with open(fpath) as f:
            return f.read()

    def write_script(self, content):
        self._conn.excute_silent(f"""
cat > {self.path} << 'EOF'
{content}
EOF
""")

    def run(self, cmd):
        self._conn.excute(cmd)


async def run_shell_content(n: N.Node):
    conn = SSHConnection(*n.get_para())
    check_order_runner = RemoteScriptRunner(conn, 'check_order.sh')
    check_seq_runner = RemoteScriptRunner(conn, 'check_seq', CHECK_SEQ)
    cmd = f"""
cd /datayes/msg_backup/{date.today().strftime('%Y%m%d')}
bash -e {check_order_runner.path} mdl_6_53_0.csv
"""
    a = conn.get_achain()
    async def task():
        await a.append_cmd(cmd)
        await a.append_cmd(f"bash -e {check_seq_runner.path} mdl_6_53_0.csv")
        await asyncio.sleep(1)
        status = await a.exit()
        utils.notify("task exit with: %s" % status)

    await a.start(asyncio.create_task(task()))
    conn.close()


async def check_redis_latency(chain: AsyncCommandChain, runner: RemoteScriptRunner):
    await chain.append_cmd(f"watch -n2 bash -e {runner.path}")
    status = await chain.exit()
    utils.notify("task exit with: %s" % status)


async def run_shell_script(file: str, node: N.Node, *task):
    """ Run the local shell script on remote node. """
    conn = SSHConnection(*node.get_para())
    runner = RemoteScriptRunner(conn, file)
    achain = conn.get_achain()
    _tasks = [t(achain, runner) for t in task]
    await achain.start(*_tasks)
    conn.close()


async def test_achain():
    conn = SSHConnection(*N.DellInspiron.get_para())
    a = conn.get_achain()
    async def task():
        await a.append_cmd("""
systemctl status wyc-ssh
q
systemctl status frpc
q
""")
        # await a.exit()

    await a.start(task())
    conn.close()



if __name__ == "__main__":
    # asyncio.run(run_shell_content(N.Prd24038))
    # asyncio.run(run_shell_script("check_redis_latency.sh", N.DellInspiron, check_redis_latency))
    asyncio.run(test_achain(), debug=True)
