input--> folder (n number of files inside the folder) / prompt(NLP) 
  |
(divide and conquer method)
  for n number of files we have n number ai agents (not lirteally)
  |
  |--> one main factor is anaylsing the interdependency between the files.
  we take inputs from all the ai agents and a final ai runs inference on all the produced results and produces the final result.


prerequisits--> count the number of files
                |
                |
                then assign that many ai agents to the files.
                |
                |
                run inferences on each and every file
                |
                |
                final ai--> final explanation (NLP)


defining the deamon process that handles the processing of interdependency between files
                                 |
                                 |
                                 |
                                 for an example--> there are 10 files, we assign 10 ai agents
                                 |
                                 |
                                 each agent will have its own precees(multiprocessing)
                                 |
                                 |
                                 shared memeory operation(queues , semaphores ,pipes,etc)
                                 |
                                 | 
                                 this way we can communicate between the processes

10 processes--> 10 ai agents
             |
             |
             10 * 9 = 90 processes * 10 = 900 communication for 10 files
             |
             |
             these 900 reuslts are shortend to 1 result by the n+1th agent.
             |
             |
             output (NLP TEXT)


recurssive prompting-->  a. load the cache of that respective file/files.
                         b. generate new infernces for the asked files.
                         c. compare and contrast the results.
                         d. get the similarties(SOP TO BE DEFINED)
                         e. generate the final result.



FRONTEND
   |
   |
   folder upload and github link upload.
   |
   |
   prompt (by the user)
   |
   |
   result


IN-SCOPE
  |
  |
  INTERACTIVE VISUALISATION