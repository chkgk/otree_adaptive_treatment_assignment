# Adaptive treatment assignment for oTree

## Overview
In this demo app, I implement weighted treatment assignment based on the number of participants that have completed each treatment. If some treatments are completed by fewer participants than others, these are dynamically over-sampled.

## Method
Treatments are not assigned at session creation. Instead, treatments are assigned when a player loads the first page of the experiment. Weighting is done based on the inverse of the distribution of players who have completed each treatment.

## Usage
Make sure to set the treatment names in the Constants. Also make sure to define a sensible threshold for the weighted treatment assignment to start in the constants (reason: see below). I think about 50% of the planned participants, is a good starting point for experimentation. 

## Limitations
There is a weakness to this method. Let's assume there are 3 treatments. Initially, all treatments are equally likely to be assigned. As soon as the first player completes the experiment, the weighting starts. Let's further assume the first player to finish is in treatment A. Thus, the weights shift such that A, B, C are now assigned with probabilities [0, 0.5, 0.5]. These stay the same until the next player completes the experiment. The problem is, that it takes time for players to reach the end of the experiment. During the time it takes the next person to finish, we only assign treatments B and C in this example. Then, suddenly, a wave of those B and C players arrive at the end of the experiment. Now, A will look under-sampled and the weights shift accordingly.

I only implement a naive way to solve the problem. We only start the weighted assignment once a threshold is reached. Before, we simply randomize treatment assignment with equal probabilities. A better way would also track the players who are currently playing (and have not dropped out) and take the treatment distribution of these players into account.