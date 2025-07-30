import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const COLORS = ["#0088FE", "#FF8042"];

function GraficoPorcentagem({ porcentagem }) {
  const data = [
    { name: "Porcentagem", value: porcentagem },
    { name: "Restante", value: 1 - porcentagem },
  ];

  return (
    <PieChart width={250} height={250}>
      <Pie
        data={data}
        cx={120}
        cy={120}
        innerRadius={60}
        outerRadius={80}
        startAngle={90}
        endAngle={-270}
        dataKey="value"
        label={({ name, value }) =>
          name === "Porcentagem" ? `${(value * 100).toFixed(1)}%` : ""
        }
      >
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
      <Legend />
    </PieChart>
  );
}

export default GraficoPorcentagem;
