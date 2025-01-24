cd C:\shared-drive\dev\llama.cpp\build
REM if you use both gpus you'll get oom on the second smaller one
set CUDA_VISIBLE_DEVICES=0
.\bin\Release\server.exe -m C:\shared-drive\llm_models\Llama-3-8B-Instruct-32k-v0.1.Q4_K_M.gguf -ngl 9999 --host 0.0.0.0 --ctx-size 32000
REM .\bin\Release\server.exe -m C:\shared-drive\llm_models\Meta-Llama-3-70B-Instruct.IQ2_XS_05132024.gguf -ngl 9999 --host 0.0.0.0
