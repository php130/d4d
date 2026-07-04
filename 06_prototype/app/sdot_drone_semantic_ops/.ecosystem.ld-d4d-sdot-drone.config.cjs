module.exports = {
  "apps": [
    {
      "name": "ld-d4d-sdot-drone",
      "script": "npm",
      "interpreter": "none",
      "args": [
        "run",
        "start"
      ],
      "cwd": "/Users/mollykim/projects/D4D/06_prototype/app/sdot_drone_semantic_ops",
      "env": {
        "PORT": "3008",
        "NODE_ENV": "production"
      },
      "autorestart": true,
      "max_restarts": 15,
      "max_memory_restart": "512M"
    }
  ]
};
