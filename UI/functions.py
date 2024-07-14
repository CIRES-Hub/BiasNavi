from metric import BiasMetrics


#identify bias
def identify_sensitive_attributes(data, target):
    metrics = BiasMetrics()
    #correlations = metrics.correlation_analysis(data, target)
    # importances = metrics.feature_importance(data, target)
    mutual_info = metrics.mutual_information(data, target)
    # chi_square = metrics.chi_square_test(data, target)
    # ks_test_results = metrics.ks_test(data, target)
    # vif = metrics.vif_analysis(data)

    #print("Correlations:\n", correlations)
    # print("Feature Importances:\n", importances)
    print("Mutual Information:\n", mutual_info)
    # print("Chi-Square Test p-values:\n", chi_square)
    # print("KS Test p-values:\n", ks_test_results)
    # print("VIF Analysis:\n", vif)