# EXPLoRa-C multithread execution benchmark

This application executes a benchmark of the Multithreaded version of the EXPLoRa-C algorithm.

Import the `java` folder inside your IDE (e.g. Netbeans, Intellij). It is a Maven project.

The main parameters to set are inside the `java/EXPLoRaCapture/src/main/java/com/lorawan/exploracapture/Main.java` file, inside the `main(...)` method.

By default the parameters are set like this:

```java
String inputFile = "/EXPLoRa-CD/python/simulation_files/100000-nodes-raw.txt";

int numberOfThreads = 4;
int repeatExecution = 10;
int numberOfNodes = 100000;
```

Change the `int numberOfThreads` to `2` or `4`. Other modes are unsupported. Threads corresponds to the number of selected base stations. The overall number of base stations is currently hardcoded (i.e. the codes assumes 200 base stations by default).

The `int repeatExecution` value represents how many times the EXPLoRa-C algorithm is executed with the same values. The input file is read the first time only. The program outputs the average execution time at the end of the consecutive executions.

The `int numberOfNodes` represents how many nodes are wrote inside the `String inputFile`. The application expects 200 basestations by default.

Change the `String inputFile` according to the path of the input file in your machine.

[//]: <> (The files with the nodes are in the following folder: https://drive.google.com/drive/folders/1DWNEL_PGTmK4I_0fYYaFRyWp6kAJAiTf?usp=sharing)

## How to run it

Execute the `main(...)` method after providing your node-file and setting your custom parameters inside.

For more technical information please refer to [HOWTO.pdf](./HOWTO.pdf)
