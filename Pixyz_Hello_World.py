import pxz

# init Pixyz
if pxz.get_current_session() == None:
    pxz.initialize()

# print Pixyz version
print(f'Pixyz version: {pxz.core.getVersion()}')

# set log level to INFO so you can see the logs in the console
pxz.core.configureInterfaceLogger(True, True, True)
pxz.core.addConsoleVerbose(core.Verbose.INFO)

