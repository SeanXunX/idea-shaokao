#!/usr/bin/env python3
"""Synthetic fresh-process adapter for testing the unattended driver only."""
import json
import sys
from engine_fixture import result_for

packet=json.load(sys.stdin)
print(json.dumps(dict(task_id=packet['task']['id'],context_sha256=packet['context_sha256'],
                      session_id='fixture-process-'+packet['task']['id'],independent=True,
                      result=result_for(packet))))
