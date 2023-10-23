CUDA_VISIBLE_DEVICES=0 python src/train_encoder_decoder.py \
    --dataset_path conic10k \
    --model_name_or_path t5-small \
    --task mathqa \
    --do_train \
    --do_eval \
    --load_in_8bit \
    --block_size 512 \
    --per_device_train_batch_size 1 \
    --num_train_epochs 20 \
    --learning_rate 8e-5 \
    --save_total_limit 3 \
    --load_best_model_at_end True \
    --save_strategy epoch \
    --evaluation_strategy epoch \
    --auto_find_batch_size \
    --output_dir . \
    --bf16