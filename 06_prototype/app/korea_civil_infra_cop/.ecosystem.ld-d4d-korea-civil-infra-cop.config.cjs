module.exports = {
  "apps": [
    {
      "name": "ld-d4d-korea-civil-infra-cop",
      "script": "npm",
      "interpreter": "none",
      "args": [
        "run",
        "start"
      ],
      "cwd": "/Users/mollykim/projects/D4D/06_prototype/app/korea_civil_infra_cop",
      "env": {
        "PORT": "3007",
        "NODE_ENV": "production"
      },
      "autorestart": true,
      "max_restarts": 15,
      "max_memory_restart": "512M"
    }
  ]
};
