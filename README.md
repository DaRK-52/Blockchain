# README

我们设计了一个 P2P 形式的区块链节点网络，每个节点都存有相同的区块链。在节点网络中，会有个 Leader 节点，用于打包区块、广播区块、维护 peer list（同伴列表）。区块中的信息以 merkle 树的形式保存。各个节点直接用 http 协议进行通信，并且我们提供了相应的网页，用于初始化节点，和查看节点以及区块链信息。

在程序运行时，每个节点会有一个主进程和守护进程。主进程用于进行区块链的基础操作，守护进程用于定期维护 peer list，并检查 Leader 是否在线。如果 Leader 掉线，其他节点（Follower）就会选举出新的 Leader 节点，确保整个网络的正常运行。

主文件为 **website.py**，可以通过以下命令启动一个节点：

``` shell
python3 website.py -a 127.0.0.1 -p 8080 -t
```

一共有三个可选参数：
* -a，--address，节点运行的IP地址，默认为 127.0.0.1
* -p，--port，节点运行的端口号，默认为 8080
* -t，--test，bool类型，如果值为 False，会生成一些文件，保存节点信息，如果为 True，则不会生成文件，便于调试。默认为 False

也可以在同一目录下编写 **config.json** 文件，来配置这三个信息。

在运行了程序后，可以通过浏览器，输入 IP 地址和端口号，如：127.0.0.1:8080，访问该节点的 **index.html** 页面，获取该节点信息。

在未初始化该节点时，页面会被重定向至 **init.html** 页面，用于初始化该节点，可以选择自己成为初始节点，也可以选择成为某个节点的 peer。

接下来将详细介绍我们的代码中的四个主要文件以及其中的一些主要函数：
* website.py：主文件，用于实现各个节点之间的通信，以及实现网页的访问
* blockchain.py：区块链节点
* daemon.py：守护进程
* util/hashTool.py：创建 merkel 树，对交易进行签名和验证

## website.py

主文件，运行时会调用 **blockchain.py** 文件，初始化区块链节点，同时也会调用 **daemon.py** 文件，新建一个守护进程。实现了各个节点间相互通信的功能，也实现了网页访问和展示的功能。

### init()

对应于文件 **templates/init.html**，用于初始化节点，可以选择 Run as Genesis Node，自己成为初始节点，也可以输入一个节点的 IP 地址和端口号，成为该节点的 peer。

### home()

对应于文件 **templates/index.html**，显示该节点的详细信息。包括：
* peer list：同伴列表
* leader info：头结点的相关信息，一般为初始节点
* node info：自己的信息
* Transaction Pool：交易池
* block info：区块链信息

### gossip()

该函数会被 blockchain.py 文件中的 gossip 函数访问，用于返回该节点信息。如果该节点为 Leader 节点，则会将访问节点加入 peer list。

### daemon()

该函数会被其他节点的守护进程访问，用于同步 peer list，并确保该节点在线。

### election()

该函数会在进行 Leader 选举时被访问。被访问时，该节点会调用 blockchain.py 文件中的 test_connection 函数，自行测试 Leader 节点是否掉线，如果该节点能连接 Leader 节点，则不参与 Leader 选举，相反则参与 Leader 选举。

## blockchain.py

包含了 BlockChain 类，是区块链节点的主文件，包含了区块链节点的主要操作，如 Leader 节点选举、交易签名、打包区块等。

### init(self, peer=None)

生成公私钥，如果指定了 peer 节点，则调用 gossip 函数，利用 peer 节点初始化自己。如果没有指定 peer 节点，则将自己设为 Leader 节点。

### gossip(self, peer)

访问 website.py 文件中的 gossip 函数，如果 peer 是 Follower，则继续访问 peer 的 Leader 的 gossip 函数，实现 Leader 信息、peer list、以及区块的同步，并将自己添加到 Leader 的 peer list 中。

### test_connection(self, peer, code)

访问 website.py 文件中的 daemon 函数，用于测试 peer 节点是否掉线。

### election(self)

用于进行新 Leader 选举。在最初建立 peer list 时会为每个节点分配一个序号（term）。选举时，节点会利用 website.py 文件中的 election 函数，用于确认序号比自己小的节点是否在线，以及是否参与选举。如果有序号比自己小的节点，则由该节点成为新的 Leader，并维护新的 peer list，反之，则自己成为新的 Leader，并维护新的 peer list。

### generate_block(self)

生成区块，区块中的内容包括了：
* index，序号
* timestamp：时间戳
* previous_hash：上一个区块的哈希值
* merkle_root：merkle 树的根
* merkle_tree：merkle 树
* block_hash：当前区块的哈希值

### verify_transaction(self, transaction)

利用 hashTool 中的 validate_signature 函数验证交易签名

## daemon.py

包含了 BcDaemon(threading.Thread) 类，创建守护进程，用于定期同步 peer list，并且检查 Leader 节点是否掉线。

### follower_daemon(self)

Follower 每过一段时间（最多5秒）会访问 Leader 节点的 website.py 中的 daemon 函数，用于获取最新的 peer list。如果 Leader 节点的信息错误，会调用 blockchain.py 文件中的 gossip 函数，重新初始化自己。如果 Leader 节点掉线，会调用 blockchain.py 文件中的 election 函数，重新选举新的节点。

### leader_daemon(self)

在 Leader 节点，会维护各个 Follower 节点的同步时间列表，如果某个 Follower 节点超过6秒没有和自己同步 peer list，则 Leader 节点会主动和该节点通信，如果发现该节点掉线，则 Leader 节点会将其从 peer list 中删除。

## util/hashTool.py

计算哈希的一些工具，是交易上链、打包区块的重要工具

### merkel_tree(data)

创建 merkel 树，实现对数据的打包

### generate_ECDSA_keys()

生成一对公私钥

### sign(private_key, data)

利用私钥对数据进行签名

### validate_signature(public_key, signature, message)

验证签名的有效性