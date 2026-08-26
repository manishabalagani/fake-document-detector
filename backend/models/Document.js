const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/db");

const Document = sequelize.define(
    "Document",
    {
        id: {
            type: DataTypes.INTEGER,
            autoIncrement: true,
            primaryKey: true
        },

        userId: {
            type: DataTypes.INTEGER,
            allowNull: false
        },

        originalName: {
            type: DataTypes.STRING,
            allowNull: false
        },

        fileName: {
            type: DataTypes.STRING,
            allowNull: false
        },

        filePath: {
            type: DataTypes.STRING,
            allowNull: false
        },

        fileType: {
            type: DataTypes.STRING,
            allowNull: true
        },

        status: {
            type: DataTypes.ENUM(
                "uploaded",
                "processing",
                "completed",
                "failed"
            ),
            defaultValue: "uploaded"
        }
    },
    {
        tableName: "documents",
        timestamps: true
    }
);

module.exports = Document;