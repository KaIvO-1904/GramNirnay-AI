export const calculateEMI = (principal: number, annualRate: number, tenureYears: number) => {
  if (principal <= 0 || annualRate <= 0 || tenureYears <= 0) return 0;
  const monthlyRate = (annualRate / 100) / 12;
  const numPayments = tenureYears * 12;
  return (principal * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) / (Math.pow(1 + monthlyRate, numPayments) - 1);
};

export const calculateBreakEven = (setupCost: number, monthlyRevenue: number, monthlyExpenses: number) => {
  const contribution = monthlyRevenue - monthlyExpenses;
  if (contribution <= 0) return 999;
  return setupCost / contribution;
};

export const calculateROI = (annualNetProfit: number, totalInvestment: number) => {
  if (totalInvestment <= 0) return 0;
  return (annualNetProfit / totalInvestment) * 100;
};
