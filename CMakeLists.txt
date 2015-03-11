# This is a hack cmake file, just to get clion to see the code
CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

Project(HACCK)
ADD_LIBRARY(hack
    STATIC
    cmph/bdz.c
    cmph/bdz_ph.c
    cmph/bmz.c
    cmph/bmz8.c
    cmph/brz.c
    cmph/buffer_entry.c
    cmph/buffer_manager.c
    cmph/chd.c
    cmph/chd_ph.c
    cmph/chm.c
    cmph/cmph.c
    cmph/cmph_benchmark.c
    cmph/cmph_structs.c
    cmph/compressed_rank.c
    cmph/compressed_seq.c
    cmph/fch.c
    cmph/fch_buckets.c
    cmph/graph.c
    cmph/hash.c
    cmph/jenkins_hash.c
    cmph/linear_string_map.c
    cmph/miller_rabin.c
    cmph/select.c
    cmph/vqueue.c
    cmph/vstack.c
)