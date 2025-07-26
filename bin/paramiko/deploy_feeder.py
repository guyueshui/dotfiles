from common import *
import time


def __deploy_by_struct(ds_struct: N.DeployStruct, conn: SSHConnection, tarname):
    """ Deploy a feeder by deploy struct. """
    bin_name, bin_dir = ds_struct.deploy_name, ds_struct.deploy_dir
    utils.notify(f"start depoly feeder({bin_name}) at {conn.host}")

    utils.notify("check root access...")
    chain = conn.get_cmd_chain().execute("sudo -i").write_input(conn.password)
    chain.execute("""
if [ "x${USER}x" != "xrootx" ]; then
    echo "I am not root, aborting..."
    exit 1
fi
""")

    utils.notify(f"deploying {bin_name} at {bin_dir}")
    chain.execute(f"""
cd {bin_dir}
while pkill -ef '{bin_name}\\b'; do sleep 1; done
echo "{bin_name} is killed!"
#mkdir -p autobak
#mv {bin_name} libmdl_api.so ./autobak
tar -xavf /home/{conn.username}/{tarname}
mv feeder_handler {bin_name}
./{bin_name}
sleep 3
if pgrep -lf '{bin_name}\\b'; then
    echo "=== deploy successed ==="
fi
""").execute("exit").execute("exit").over()
    time.sleep(1)


def deploy_feeder_by_ds(node_cls: N.Node, *args: N.DeployStruct):
    conn = SSHConnection(*node_cls.get_para())

    # transfer
    tarname = "feeder_handler.tar.bz2"
    if transfer_feeder_to(node_cls, tarname) != 0:
        utils.notify("transfer failed, aborting...")
        return False

    # test
    utils.notify("test file existence at", node_cls.get_desc())
    conn.excute(f"""
if [ ! -f {tarname} ]; then
    echo "File not found, aborting..."
    exit 1
else
    echo "File found, testing..."
fi
""")

    # deploy
    time.sleep(1)
    for ds in args:
        print('\n')
        __deploy_by_struct(ds, conn, tarname)
        print('\n')
    time.sleep(1)
    conn.close()


if __name__ == "__main__":
    # deploy_feeder_by_ds(N.RedisFwdDev, N.RedisFwdDev.DS_LIST[0])
    # deploy_feeder_by_ds(N.RedisFwdDev, *N.RedisFwdDev.DS_LIST)
    deploy_feeder_by_ds(N.BarDev, N.BarDev.DS)