using System;
using System.Data;
using System.Collections.Generic;

namespace Cpmf.Config
{
    /// <summary>Root configuration object.</summary>
    public class CodedConfig
    {
        public SettingsConfig Settings { get; set; } = new();
        public ConstantsConfig Constants { get; set; } = new();
        public AssetsConfig Assets { get; set; } = new();
        public override string ToString() =>
            $"CodedConfig {{ Settings={Settings}, Constants={Constants}, Assets={Assets} }}";

        public static CodedConfig Load(Dictionary<string, DataTable> tables)
        {
            var cfg = new CodedConfig();
            if (tables.TryGetValue("Settings", out var t_Settings)) cfg.Settings = SettingsConfig.FromDataTable(t_Settings);
            if (tables.TryGetValue("Constants", out var t_Constants)) cfg.Constants = ConstantsConfig.FromDataTable(t_Constants);
            return cfg;
        }
    }

    public class SettingsConfig
    {
        /// <summary>string</summary>
        public string FeatureName { get; set; } = "";
        /// <summary>int</summary>
        public int MaxItems { get; set; }
        /// <summary>double</summary>
        public double Threshold { get; set; }
        /// <summary>bool</summary>
        public bool IsEnabled { get; set; }
        /// <summary>DateOnly — date only, time is 00:00:00</summary>
        public DateOnly CutoffDate { get; set; }
        /// <summary>DateTime — has time component</summary>
        public DateTime ScheduledAt { get; set; }
        /// <summary>TimeOnly — time only, no date</summary>
        public TimeOnly DailyRunTime { get; set; }

        public static SettingsConfig FromDataTable(DataTable dt)
        {
            var cfg = new SettingsConfig();
            foreach (DataRow row in dt.Rows)
            {
                var key   = row[0]?.ToString()?.Trim();
                var value = row[1]?.ToString()?.Trim() ?? "";
                switch (key)
                {
                    case "FeatureName": cfg.FeatureName = value; break;
                    case "MaxItems":
                        if (int.TryParse(value, out var v_MaxItems)) cfg.MaxItems = v_MaxItems;
                        break;
                    case "Threshold":
                        if (double.TryParse(value, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out var v_Threshold)) cfg.Threshold = v_Threshold;
                        break;
                    case "IsEnabled":
                        if (bool.TryParse(value, out var v_IsEnabled)) cfg.IsEnabled = v_IsEnabled;
                        break;
                    case "CutoffDate":
                        if (DateOnly.TryParse(value, out var v_CutoffDate)) cfg.CutoffDate = v_CutoffDate;
                        break;
                    case "ScheduledAt":
                        if (DateTime.TryParse(value, out var v_ScheduledAt)) cfg.ScheduledAt = v_ScheduledAt;
                        break;
                    case "DailyRunTime":
                        if (TimeOnly.TryParse(value, out var v_DailyRunTime)) cfg.DailyRunTime = v_DailyRunTime;
                        break;
                }
            }
            return cfg;
        }
    }

    public class ConstantsConfig
    {
        /// <summary>double — mathematical constant</summary>
        public double Pi { get; set; }
        /// <summary>int</summary>
        public int MaxRetryNumber { get; set; }
        /// <summary>bool</summary>
        public bool StrictMode { get; set; }
        /// <summary>DateOnly</summary>
        public DateOnly ExpiresOn { get; set; }
        /// <summary>DateTime</summary>
        public DateTime CreatedAt { get; set; }
        /// <summary>TimeOnly</summary>
        public TimeOnly WindowOpen { get; set; }
        /// <summary>TimeOnly</summary>
        public TimeOnly WindowClose { get; set; }

        public static ConstantsConfig FromDataTable(DataTable dt)
        {
            var cfg = new ConstantsConfig();
            foreach (DataRow row in dt.Rows)
            {
                var key   = row[0]?.ToString()?.Trim();
                var value = row[1]?.ToString()?.Trim() ?? "";
                switch (key)
                {
                    case "Pi":
                        if (double.TryParse(value, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out var v_Pi)) cfg.Pi = v_Pi;
                        break;
                    case "MaxRetryNumber":
                        if (int.TryParse(value, out var v_MaxRetryNumber)) cfg.MaxRetryNumber = v_MaxRetryNumber;
                        break;
                    case "StrictMode":
                        if (bool.TryParse(value, out var v_StrictMode)) cfg.StrictMode = v_StrictMode;
                        break;
                    case "ExpiresOn":
                        if (DateOnly.TryParse(value, out var v_ExpiresOn)) cfg.ExpiresOn = v_ExpiresOn;
                        break;
                    case "CreatedAt":
                        if (DateTime.TryParse(value, out var v_CreatedAt)) cfg.CreatedAt = v_CreatedAt;
                        break;
                    case "WindowOpen":
                        if (TimeOnly.TryParse(value, out var v_WindowOpen)) cfg.WindowOpen = v_WindowOpen;
                        break;
                    case "WindowClose":
                        if (TimeOnly.TryParse(value, out var v_WindowClose)) cfg.WindowClose = v_WindowClose;
                        break;
                }
            }
            return cfg;
        }
    }

    public class AssetsConfig
    {
        // No data rows found in source sheet.
    }
}