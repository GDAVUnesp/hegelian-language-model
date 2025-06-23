

import os
import json
import random
# random.seed(0)
from code.utils.agent import Agent

NAME_LIST=[
    "Affirmative side",
    "Negative side",
    "Moderator",
]

class DebatePlayer(Agent):
    def __init__(self, model_name: str, name: str, temperature:float, sleep_time: float) -> None:
        """Create a player in the debate

        Args:
            model_name(str): model name
            name (str): name of this player
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            openai_api_key (str): As the parameter name suggests
            sleep_time (float): sleep because of rate limits
        """
        super(DebatePlayer, self).__init__(model_name, name, temperature, sleep_time)
        #self.openai_api_key = openai_api_key


class Debate:
    def __init__(self,
            model_name: str='gemma:2b', 
            temperature: float=0.7, 
            num_players: int=7, 
            #openai_api_key: str=None,
            config: dict=None,
            max_round: int=3,
            sleep_time: float=0
        ) -> None:
        """Create a debate

        Args:
            model_name (str): openai model name
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            num_players (int): num of players
            openai_api_key (str): As the parameter name suggests
            max_round (int): maximum Rounds of Debate
            sleep_time (float): sleep because of rate limits
        """

        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        #self.openai_api_key = openai_api_key
        self.config = config
        self.max_round = max_round
        self.sleep_time = sleep_time

        self.init_prompt()

        # creat&init agents
        self.creat_agents()
        self.init_agents()


    def init_prompt(self):
        def prompt_replace(key):
            self.config[key] = self.config[key].replace("##debate_topic##", self.config["debate_topic"])
        prompt_replace("player_meta_prompt")
        prompt_replace("moderator_meta_prompt")
        prompt_replace("affirmative_prompt")
        prompt_replace("judge1_prompt_last2")
        prompt_replace("judge2_prompt_last2")
        prompt_replace("judge3_prompt_last2")
        prompt_replace("judge4_prompt_last2")        
        prompt_replace("judge5_prompt_last2")


    def creat_agents(self):
        # creates players
        self.players = [
            DebatePlayer(model_name=self.model_name, name=name, temperature=self.temperature, sleep_time=self.sleep_time) for name in NAME_LIST
        ]
        self.affirmative = self.players[0]
        self.negative = self.players[1]
        self.moderator = self.players[2]

    def init_agents(self):
        # Set meta prompts
        self.affirmative.set_meta_prompt(self.config['player_meta_prompt'])
        self.negative.set_meta_prompt(self.config['player_meta_prompt'])
        self.moderator.set_meta_prompt(self.config['moderator_meta_prompt'])

        # Round 1: Opinions
        print(f"===== Debate Round-1 =====\n")
        self.affirmative.add_event(self.config['affirmative_prompt'])
        self.aff_ans = self.affirmative.ask()
        self.affirmative.add_memory(self.aff_ans)
        self.config['base_answer'] = self.aff_ans

        self.negative.add_event(self.config['negative_prompt'].replace('##aff_ans##', self.aff_ans))
        self.neg_ans = self.negative.ask()
        self.negative.add_memory(self.neg_ans)

        self.moderator.add_event(
            self.config['moderator_prompt']
                .replace('##aff_ans##', self.aff_ans)
                .replace('##neg_ans##', self.neg_ans)
                .replace('##round##', 'first')
        )

        raw_response = self.moderator.ask()
        self.moderator.add_memory(raw_response)

        # Clean JSON string if wrapped in markdown code block
        cleaned = raw_response.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:-1])

        try:
            self.mod_ans = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to decode JSON from moderator response:\n{cleaned}\nError: {e}")
            self.mod_ans = {"debate_answer": "", "Reason": "Failed to parse moderator response."}

    def round_dct(self, num: int):
        dct = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
        }
        return dct[num]

    def print_answer(self):
        print("\n\n===== Debate Done! =====")
        print("\n----- Debate Topic -----")
        print(self.config["debate_topic"])
        print("\n----- Base Answer -----")
        print(self.config["base_answer"])
        print("\n----- Debate Answer -----")
        print(self.config["debate_answer"])
        #print("\n----- Debate Reason -----")
        #print(self.config["Reason"])

    def broadcast(self, msg: str):
        """Broadcast a message to all players. 
        Typical use is for the host to announce public information

        Args:
            msg (str): the message
        """
        # print(msg)
        for player in self.players:
            player.add_event(msg)

    def speak(self, speaker: str, msg: str):
        """The speaker broadcast a message to all other players. 

        Args:
            speaker (str): name of the speaker
            msg (str): the message
        """
        if not msg.startswith(f"{speaker}: "):
            msg = f"{speaker}: {msg}"
        # print(msg)
        for player in self.players:
            if player.name != speaker:
                player.add_event(msg)

    def ask_and_speak(self, player: DebatePlayer):
        ans = player.ask()
        player.add_memory(ans)
        self.speak(player.name, ans)

    def run(self):
        for round in range(self.max_round - 1):
            if isinstance(self.mod_ans, dict) and self.mod_ans.get("debate_answer", '') != '':
                break
            else:
                print(f"===== Debate Round-{round+2} =====\n")
                self.affirmative.add_event(self.config['debate_prompt'].replace('##oppo_ans##', self.neg_ans))
                self.aff_ans = self.affirmative.ask()
                self.affirmative.add_memory(self.aff_ans)

                self.negative.add_event(self.config['debate_prompt'].replace('##oppo_ans##', self.aff_ans))
                self.neg_ans = self.negative.ask()
                self.negative.add_memory(self.neg_ans)

                self.moderator.add_event(
                    self.config['moderator_prompt']
                        .replace('##aff_ans##', self.aff_ans)
                        .replace('##neg_ans##', self.neg_ans)
                        .replace('##round##', self.round_dct(round + 2))
                )
                self.mod_ans = self.moderator.ask()
                self.moderator.add_memory(self.mod_ans)

                try:
                    self.mod_ans = eval(self.mod_ans)
                except:
                    self.mod_ans = {"debate_answer": "", "Reason": ""}

        # Final judgment by 5 judges
        aff_ans = self.affirmative.memory_lst[2]['content']
        neg_ans = self.negative.memory_lst[2]['content']

        final_votes = []
        vote_summary = {}
        judge_reasons = []

        for i in range(1, 6):
            judge_name = f'Judge {i}'
            judge = DebatePlayer(
                model_name=self.model_name,
                name=judge_name,
                temperature=self.temperature,
                #openai_api_key=self.openai_api_key,
                sleep_time=self.sleep_time
            )
            self.players.append(judge)

            # Set meta-prompt
            judge.set_meta_prompt(self.config['moderator_meta_prompt'])

            # Step 1: Present candidates
            judge_prompt1 = self.config[f'judge{i}_prompt_last1']
            judge.add_event(judge_prompt1.replace('##aff_ans##', aff_ans).replace('##neg_ans##', neg_ans))
            _ = judge.ask()

            # Step 2: Final reasoning
            judge_prompt2 = self.config[f'judge{i}_prompt_last2']
            judge.add_event(judge_prompt2.replace('##debate_topic##', self.config["debate_topic"]))
            judge_json = judge.ask()
            judge.add_memory(judge_json)

            try:
                result = json.loads(judge_json)
                reason = result.get("Reason", "").strip()
                answer = result.get("debate_answer", "").strip()
                judge_reasons.append((judge_name, reason, answer))
            except:
                judge_reasons.append((judge_name, "[Invalid JSON]", "[No answer]"))

            # Step 3: Ask for final vote (yes/no)
            judge.add_event("Do you believe the final answer of the debate makes logical sense and is clearly reasoned? Reply only with 'Yes' or 'No'.")
            vote = judge.ask().strip().lower()
            final_votes.append(vote)
            vote_summary[judge_name] = vote

        # Count votes
        yes_votes = sum(1 for vote in final_votes if 'yes' in vote)
        no_votes = 5 - yes_votes

        # Final result
        self.config['final_votes'] = vote_summary
        self.config['final_decision'] = "Accepted" if yes_votes >= 3 else "Rejected"
        self.config['success'] = True

        # Display judge decisions
        print("\n===== Judges' Reasoning and Votes =====")
        for name, reason, answer in judge_reasons:
            print(f"\n{name}:\n- Final Answer: {answer}\n- Reason: {reason}")
            print(f"- Vote: {vote_summary[name].capitalize()}")

        # Final verdict
        print("\n===== Final Decision =====")
        print(f"Votes: {yes_votes} Yes / {no_votes} No")
        print(f"Conclusion: {'Makes sense' if yes_votes >= 3 else 'Does NOT make sense'}")

        self.print_answer()

if __name__ == "__main__":
    current_script_path = os.path.abspath(__file__)
    MAD_path = os.path.dirname(current_script_path)

    while True:
        debate_topic = ""
        while not debate_topic.strip():
            debate_topic = input(f"\nEnter your debate topic: ")

        config_path = os.path.join(MAD_path, "code", "utils", "config4all.json")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["debate_topic"] = debate_topic

        # Debate using Gemma3:4B loaded via Ollama
        debate = Debate(
            #model_name="gemma3:4b",
            model_name="gemma:2b",           
            num_players=7,
            config=config,
            temperature=0.7,
            sleep_time=0
        )
        debate.run()
