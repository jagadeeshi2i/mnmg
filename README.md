# mnmg

python -m torch.distributed.run --nnodes=2 --master_addr "172.31.60.130" --master_port 12356 --node_rank 0 bert.py --strategy=ddp --num_nodes=2 --gpus=1 --max_epochs=15
