Pontos de atenção: 

A temperatura influencia em todos os agentes, nos agentes tese/antítese com temperatura 0, os mesmos criam respostas mais nebulosas, sem posicionamento, mesmo colocando perguntas de resposta óbvia ou evidencias logicas. Isso pode refletir o comportamento padrão de uma LLM, no qual sempre tenta concordar com a proposta (referência: large language models are not naysayers). Nos juízes, a temperatura = 0 influencia negativamente a criatividade, fazendo com que todos tenham um comportamento igual ou muito parecido, dando respostas idênticas.

- Necessário implementar o sistema de Rounds adequadamente.
- Testado com gemma3:4b e gemma:2b (pressupôe que todos os modelos Ollama funcionem nessa arquitetura).
- Fazer a análise com o Benchmark Results do gemma3 em Ollama (consta uns já avaliados como MMLU e GSM8K).
- Verificar a ação do moderador, se ele apenas escolhe uma das respostas como tese ou antítese ou faz a mescla das duas. 
- Verificar o parâmetro: number of players
- Verificar a complexidade da resposta quando o agente antitese sabe que está contra argumentando uma IA
