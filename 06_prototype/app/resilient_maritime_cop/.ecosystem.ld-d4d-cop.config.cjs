module.exports = {
  "apps": [
    {
      "name": "ld-d4d-cop",
      "script": "npm",
      "interpreter": "none",
      "args": [
        "run",
        "start"
      ],
      "cwd": "/Users/mollykim/projects/D4D/06_prototype/app/resilient_maritime_cop",
      "env": {
        "PORT": "3005",
        "NODE_ENV": "production"
      },
      "autorestart": true,
      "max_restarts": 15,
      "max_memory_restart": "512M"
    }
  ]
};
