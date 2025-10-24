// Configure dotenv with the path to the .env file
require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });

const mongoose = require('mongoose');
const connectDB = require('../config/db');
const Teacher = require('../models/Teacher');
const Student = require('../models/Student');

const teachers = [
  {
    name: 'MKS Faculty',
    email: 'mks.mca@psgtech.ac.in',
    password: 'mks',
  },
  {
    name: 'NKS Faculty',
    email: 'nks.mca@gmail.com',
    password: 'nks',
  },
];

const students = [
 
  {
    name: 'Manikandan KS',
    rollno: '24MX112',
    batch: '2024-MX-G1',
    email: '24mx112@psgtech.ac.in',
    password: '123',
  },
  {
    name: 'Niresh Kumar S',
    rollno: '24MX118',
    batch: '2024-MX-G1',
    email: '24mx118@psgtech.ac.in',
    password: '123',
  },
];

async function upsertDocuments(model, records, identifier) {
  const results = [];

  for (const record of records) {
    const filter = {};
    for (const field of identifier) {
      filter[field] = record[field];
    }

    const doc = await model.findOneAndUpdate(
      filter,
      { $setOnInsert: record },
      { new: true, upsert: true }
    );

    const created = identifier.every((field) => doc[field] === record[field]);
    results.push({ record, created });
  }

  return results;
}

async function run() {
  try {
    await connectDB();

    const teacherResults = await upsertDocuments(Teacher, teachers, ['email']);
    const studentResults = await upsertDocuments(Student, students, ['email']);

    for (const { record, created } of teacherResults) {
      // eslint-disable-next-line no-console
      console.log(`${created ? 'Created' : 'Found existing'} teacher: ${record.email}`);
    }

    for (const { record, created } of studentResults) {
      // eslint-disable-next-line no-console
      console.log(`${created ? 'Created' : 'Found existing'} student: ${record.email}`);
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Seeding failed:', error.message);
  } finally {
    await mongoose.disconnect();
  }
}

run();
