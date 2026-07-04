module.exports = {
  "apps": [
    {
      "name": "ld-d4d-drone-production-conversion",
      "script": "npm",
      "interpreter": "none",
      "args": [
        "run",
        "start"
      ],
      "cwd": "/Users/mollykim/projects/D4D/06_prototype/app/drone_production_conversion",
      "env": {
        "PORT": "3009",
        "NODE_ENV": "production"
      },
      "autorestart": true,
      "max_restarts": 15,
      "max_memory_restart": "512M"
    }
  ]
};
