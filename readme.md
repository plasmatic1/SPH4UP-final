# SPH4UP - Summative

Problem: Modified version of IYPT 1988 Problem 4

Given a circuit of perfect batteries, resistors, and wires along with a pair of junctions, compute the potential difference between the junctions.

## General Approach

* Treat batteries independently and sum values
* Direct edges based on conventional current
* Run Interval-like-DP based on nodes to find resistances of components (bottom-up)
* Repeat to find potential difference (but this time, top-down)

Overall time complexity is quadratic (O(NM) I think) per battery, so cubic in the worst case.

## Input Format

Arguments: `python3 <circuit file name>`

### Circuit File Format

Every line except for the last one should be one of the following:

```
battery <id> <emf>
junction <id>
resistor <id> <resistance>
connect <id1> <id2>
```

* EMF is in Volts
* Resistance is in Ohms
* Edges are undirected
* Battery command creates two nodes, `<id>+` and `<id>-`
* Resistor command creates one node `<id>`
* Junction command creates one node `<id>`
* Note that for `connect <id1> <id2>` to work, the nodes `<id1>` and `<id2>` should already have been declared

The last line should always be in the format `<id1> <id2>`, denoting the pair of junctions you want to measure the potential difference of.