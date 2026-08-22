const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/db");

const Analysis = sequelize.define(
    "Analysis",
    {
        id: {
            type: DataTypes.INTEGER,
            autoIncrement: true,
            primaryKey: true
        },

        documentId: {
            type: DataTypes.INTEGER,
            allowNull: false
        },

        result: {
            type: DataTypes.ENUM("fake", "genuine", "suspicious"),
            allowNull: false
        },

        confidence: {
            type: DataTypes.FLOAT,
            allowNull: false
        },

        reason: {
            type: DataTypes.TEXT,
            allowNull: true
        },

        analyzedAt: {
            type: DataTypes.DATE,
            defaultValue: DataTypes.NOW
        }
    },
    {
        tableName: "analyses",
        timestamps: true
    }
);

module.exports = Analysis;