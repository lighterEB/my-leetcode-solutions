use std::collections::HashMap;
impl Solution {
    pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
        let mut map: HashMap<i32, usize> = HashMap::new();
        for (index, &num) in nums.iter().enumerate() {
            if let Some(&r) = map.get(&(target - num)) {
                return vec![r as i32, index as i32];
            }
            map.insert(num, index);
        }

        vec![]
    }
}
