import kyukou
import sys
import codecs
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

kyukou.run_server(port=5426)
